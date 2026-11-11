from django.db import migrations

PRESENTES_INICIAIS = [
    {'nome': 'Jogo de panelas', 'descricao': 'Para os primeiros almoços de casados', 'valor': '250.00', 'emoji': '🍳', 'ordem': 1},
    {'nome': 'Liquidificador', 'descricao': 'Vitaminas e sucos no café da manhã', 'valor': '180.00', 'emoji': '🥤', 'ordem': 2},
    {'nome': 'Jogo de cama casal', 'descricao': 'Noites de sono mais confortáveis', 'valor': '220.00', 'emoji': '🛏️', 'ordem': 3},
    {'nome': 'Jogo de toalhas', 'descricao': 'Para o banheiro novo', 'valor': '150.00', 'emoji': '🧺', 'ordem': 4},
    {'nome': 'Air fryer', 'descricao': 'Praticidade no dia a dia', 'valor': '400.00', 'emoji': '🍟', 'ordem': 5},
    {'nome': 'Cafeteira', 'descricao': 'Café fresquinho todo dia', 'valor': '200.00', 'emoji': '☕', 'ordem': 6},
    {'nome': 'Jantar romântico', 'descricao': 'Uma noite especial só dos dois', 'valor': '150.00', 'emoji': '🍷', 'ordem': 7},
    {'nome': 'Cota lua de mel', 'descricao': 'Ajuda para a viagem dos sonhos', 'valor': '300.00', 'emoji': '✈️', 'ordem': 8},
    {'nome': 'Kit churrasco', 'descricao': 'Para receber a família e os amigos', 'valor': '180.00', 'emoji': '🍖', 'ordem': 9},
    {'nome': 'Aspirador de pó', 'descricao': 'Casa novinha sempre em ordem', 'valor': '350.00', 'emoji': '🧹', 'ordem': 10},
]


def criar_presentes(apps, schema_editor):
    Presente = apps.get_model('rsvp', 'Presente')
    for item in PRESENTES_INICIAIS:
        Presente.objects.get_or_create(nome=item['nome'], defaults=item)


def remover_presentes(apps, schema_editor):
    Presente = apps.get_model('rsvp', 'Presente')
    nomes = [item['nome'] for item in PRESENTES_INICIAIS]
    Presente.objects.filter(nome__in=nomes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('rsvp', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(criar_presentes, remover_presentes),
    ]
