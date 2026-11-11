from django.db import models
from django.utils import timezone


class Confirmacao(models.Model):
    SIM = 'sim'
    NAO = 'nao'
    OPCOES_PRESENCA = [
        (SIM, 'Sim, vou estar lá! 🎉'),
        (NAO, 'Infelizmente não poderei ir 😢'),
    ]

    nome = models.CharField('Seu nome', max_length=200)
    email = models.EmailField('Seu e-mail', blank=True)
    telefone = models.CharField('Telefone / WhatsApp', max_length=30, blank=True)
    presenca = models.CharField('Vai comparecer?', max_length=3, choices=OPCOES_PRESENCA, default=SIM)
    acompanhantes = models.TextField(
        'Nome dos acompanhantes',
        blank=True,
        help_text='Coloque um nome por linha, se for levar acompanhantes.'
    )
    mensagem = models.TextField('Mensagem para os noivos', blank=True)
    criado_em = models.DateTimeField('Enviado em', auto_now_add=True)

    class Meta:
        verbose_name = 'Confirmação de presença'
        verbose_name_plural = 'Confirmações de presença'
        ordering = ['-criado_em']

    def __str__(self):
        return f'{self.nome} ({self.get_presenca_display()})'

    def lista_acompanhantes(self):
        """Retorna a lista de acompanhantes, um nome por linha, já limpa."""
        return [linha.strip() for linha in self.acompanhantes.splitlines() if linha.strip()]

    def total_pessoas(self):
        if self.presenca == self.NAO:
            return 0
        return 1 + len(self.lista_acompanhantes())


class Presente(models.Model):
    nome = models.CharField('Nome do presente', max_length=150)
    descricao = models.CharField('Descrição curta', max_length=250, blank=True)
    valor = models.DecimalField('Valor (R$)', max_digits=8, decimal_places=2)
    emoji = models.CharField(
        'Emoji/ícone', max_length=10, default='🎁',
        help_text='Um emoji para representar o presente na lista, ex: 🍽️ 🧺 ✈️'
    )
    ordem = models.PositiveIntegerField('Ordem de exibição', default=0)
    reservado = models.BooleanField('Já foi escolhido?', default=False)
    reservado_por = models.CharField('Escolhido por', max_length=200, blank=True)
    reservado_em = models.DateTimeField('Escolhido em', null=True, blank=True)

    class Meta:
        verbose_name = 'Presente'
        verbose_name_plural = 'Lista de presentes'
        ordering = ['reservado', 'ordem', 'nome']

    def __str__(self):
        status = 'reservado' if self.reservado else 'disponível'
        return f'{self.emoji} {self.nome} (R$ {self.valor}) - {status}'

    def marcar_como_reservado(self, nome_convidado):
        self.reservado = True
        self.reservado_por = nome_convidado
        self.reservado_em = timezone.now()
        self.save()
