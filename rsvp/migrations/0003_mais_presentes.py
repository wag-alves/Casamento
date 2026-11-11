from django.db import migrations

NOVOS_PRESENTES = [
    {'nome': 'Video game', 'descricao': 'Para as noites de diversão do casal', 'valor': '2500.00', 'emoji': '🎮', 'ordem': 11},
    {'nome': 'Casinha do cachorro', 'descricao': 'Um cantinho confortável para o nosso pet', 'valor': '280.00', 'emoji': '🐶', 'ordem': 12},
    {'nome': 'Smart TV', 'descricao': 'Para as maratonas de séries a dois', 'valor': '1800.00', 'emoji': '📺', 'ordem': 13},
    {'nome': 'Jogo de taças', 'descricao': 'Para brindar cada conquista', 'valor': '160.00', 'emoji': '🥂', 'ordem': 14},
    {'nome': 'Ventilador', 'descricao': 'Para aguentar o calor de Natal', 'valor': '230.00', 'emoji': '🌀', 'ordem': 15},
    {'nome': 'Ração e petiscos do pet', 'descricao': 'Para mimar o nosso cachorro', 'valor': '120.00', 'emoji': '🦴', 'ordem': 16},
]


def criar_presentes(apps, schema_editor):
    Presente = apps.get_model('rsvp', 'Presente')
    for item in NOVOS_PRESENTES:
        Presente.objects.get_or_create(nome=item['nome'], defaults=item)


def remover_presentes(apps, schema_editor):
    Presente = apps.get_model('rsvp', 'Presente')
    Presente.objects.filter(nome__in=[i['nome'] for i in NOVOS_PRESENTES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('rsvp', '0002_presentes_iniciais'),
    ]

    operations = [
        migrations.RunPython(criar_presentes, remover_presentes),
    ]
