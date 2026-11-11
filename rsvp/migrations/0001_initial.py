from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Confirmacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200, verbose_name='Seu nome')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Seu e-mail')),
                ('telefone', models.CharField(blank=True, max_length=30, verbose_name='Telefone / WhatsApp')),
                ('presenca', models.CharField(
                    choices=[('sim', 'Sim, vou estar lá! 🎉'), ('nao', 'Infelizmente não poderei ir 😢')],
                    default='sim', max_length=3, verbose_name='Vai comparecer?'
                )),
                ('acompanhantes', models.TextField(
                    blank=True,
                    help_text='Coloque um nome por linha, se for levar acompanhantes.',
                    verbose_name='Nome dos acompanhantes'
                )),
                ('mensagem', models.TextField(blank=True, verbose_name='Mensagem para os noivos')),
                ('criado_em', models.DateTimeField(auto_now_add=True, verbose_name='Enviado em')),
            ],
            options={
                'verbose_name': 'Confirmação de presença',
                'verbose_name_plural': 'Confirmações de presença',
                'ordering': ['-criado_em'],
            },
        ),
        migrations.CreateModel(
            name='Presente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150, verbose_name='Nome do presente')),
                ('descricao', models.CharField(blank=True, max_length=250, verbose_name='Descrição curta')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Valor (R$)')),
                ('emoji', models.CharField(
                    default='🎁', help_text='Um emoji para representar o presente na lista, ex: 🍽️ 🧺 ✈️',
                    max_length=10, verbose_name='Emoji/ícone'
                )),
                ('ordem', models.PositiveIntegerField(default=0, verbose_name='Ordem de exibição')),
                ('reservado', models.BooleanField(default=False, verbose_name='Já foi escolhido?')),
                ('reservado_por', models.CharField(blank=True, max_length=200, verbose_name='Escolhido por')),
                ('reservado_em', models.DateTimeField(blank=True, null=True, verbose_name='Escolhido em')),
            ],
            options={
                'verbose_name': 'Presente',
                'verbose_name_plural': 'Lista de presentes',
                'ordering': ['reservado', 'ordem', 'nome'],
            },
        ),
    ]
