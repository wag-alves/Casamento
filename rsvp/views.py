import io

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import ConfirmacaoForm, ReservaPresenteForm
from .models import Presente
from .pix import gerar_payload_pix

NOIVOS = 'Larissa & Wagner'
DATA_CASAMENTO = '10 de Junho de 2027'
HORARIO = '15h30'
LOCAL = 'Natal - RN'


# ---------------------------------------------------------------------------
# Home / RSVP
# ---------------------------------------------------------------------------
def home(request):
    if request.method == 'POST':
        form = ConfirmacaoForm(request.POST)
        if form.is_valid():
            confirmacao = form.save()
            _enviar_email_confirmacao(confirmacao)
            messages.success(request, 'Presença confirmada com sucesso! Obrigado, ' + confirmacao.nome + '!')
            return redirect('obrigado')
    else:
        form = ConfirmacaoForm()

    contexto = {
        'form': form,
        'noivos': NOIVOS,
        'data_casamento': DATA_CASAMENTO,
        'horario': HORARIO,
        'local': LOCAL,
    }
    return render(request, 'rsvp/home.html', contexto)


def obrigado(request):
    return render(request, 'rsvp/obrigado.html')


def _enviar_email_confirmacao(confirmacao):
    """Envia um e-mail para os noivos toda vez que alguém confirma presença."""
    acompanhantes = confirmacao.lista_acompanhantes()

    linhas = [
        'Nova confirmação de presença recebida no site do casamento!',
        '',
        f'Nome: {confirmacao.nome}',
        f'Vai comparecer: {confirmacao.get_presenca_display()}',
    ]

    if confirmacao.email:
        linhas.append(f'E-mail: {confirmacao.email}')
    if confirmacao.telefone:
        linhas.append(f'Telefone: {confirmacao.telefone}')

    if acompanhantes:
        linhas.append('')
        linhas.append('Acompanhantes:')
        for nome in acompanhantes:
            linhas.append(f'  - {nome}')
    else:
        linhas.append('')
        linhas.append('Sem acompanhantes.')

    linhas.append('')
    linhas.append(f'Total de pessoas: {confirmacao.total_pessoas()}')

    if confirmacao.mensagem:
        linhas.append('')
        linhas.append('Mensagem:')
        linhas.append(confirmacao.mensagem)

    send_mail(
        subject=f'[Save the Date] Confirmação de {confirmacao.nome}',
        message='\n'.join(linhas),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.NOTIFICATION_EMAIL],
        fail_silently=True,
    )


# ---------------------------------------------------------------------------
# Lista de presentes (Pix)
# ---------------------------------------------------------------------------
def presentes(request):
    lista = Presente.objects.all()
    contexto = {
        'presentes': lista,
        'noivos': NOIVOS,
    }
    return render(request, 'rsvp/presentes.html', contexto)


def presente_detail(request, pk):
    presente = get_object_or_404(Presente, pk=pk)

    if request.method == 'POST' and not presente.reservado:
        form = ReservaPresenteForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Trava a linha para evitar duas pessoas reservando o mesmo item ao mesmo tempo
                presente_travado = Presente.objects.select_for_update().get(pk=presente.pk)
                if presente_travado.reservado:
                    messages.error(request, 'Ops! Alguém acabou de escolher esse presente. Veja outras opções.')
                    return redirect('presentes')
                presente_travado.marcar_como_reservado(form.cleaned_data['nome'])

            _enviar_email_presente(presente_travado, form.cleaned_data.get('mensagem', ''))
            return redirect('presente_obrigado')
    else:
        form = ReservaPresenteForm()

    payload_pix = gerar_payload_pix(
        chave=settings.PIX_KEY,
        nome=settings.PIX_NOME,
        cidade=settings.PIX_CIDADE,
        valor=presente.valor,
        txid=f'PRESENTE{presente.pk}',
        descricao=presente.nome,
    )

    contexto = {
        'presente': presente,
        'form': form,
        'pix_chave': settings.PIX_KEY,
        'pix_payload': payload_pix,
        'noivos': NOIVOS,
    }
    return render(request, 'rsvp/presente_detail.html', contexto)


def presente_qrcode(request, pk):
    """Gera dinamicamente a imagem do QR Code Pix para o presente escolhido."""
    presente = get_object_or_404(Presente, pk=pk)

    try:
        import qrcode
    except ImportError:
        return HttpResponse('Biblioteca "qrcode" não instalada. Rode: pip install qrcode[pil]', status=500)

    payload = gerar_payload_pix(
        chave=settings.PIX_KEY,
        nome=settings.PIX_NOME,
        cidade=settings.PIX_CIDADE,
        valor=presente.valor,
        txid=f'PRESENTE{presente.pk}',
        descricao=presente.nome,
    )
    img = qrcode.make(payload, box_size=8, border=2)
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')


def presente_obrigado(request):
    return render(request, 'rsvp/presente_obrigado.html')


def _enviar_email_presente(presente, mensagem):
    linhas = [
        'Alguém escolheu um presente da lista do casamento!',
        '',
        f'Presente: {presente.emoji} {presente.nome} (R$ {presente.valor})',
        f'Escolhido por: {presente.reservado_por}',
    ]
    if mensagem:
        linhas.append('')
        linhas.append('Mensagem:')
        linhas.append(mensagem)

    send_mail(
        subject=f'[Lista de Presentes] {presente.reservado_por} escolheu "{presente.nome}"',
        message='\n'.join(linhas),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.NOTIFICATION_EMAIL],
        fail_silently=True,
    )
