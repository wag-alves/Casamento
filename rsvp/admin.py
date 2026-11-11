from django.contrib import admin
from .models import Confirmacao, Presente


@admin.register(Confirmacao)
class ConfirmacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'presenca', 'total_pessoas', 'criado_em')
    list_filter = ('presenca',)
    search_fields = ('nome', 'email', 'acompanhantes')
    readonly_fields = ('criado_em',)


@admin.register(Presente)
class PresenteAdmin(admin.ModelAdmin):
    list_display = ('emoji', 'nome', 'valor', 'reservado', 'reservado_por', 'reservado_em', 'ordem')
    list_filter = ('reservado',)
    list_editable = ('ordem',)
    search_fields = ('nome', 'reservado_por')
    readonly_fields = ('reservado_em',)
