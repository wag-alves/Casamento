from rest_framework import serializers
from .models import Confirmacao, Presente


class ConfirmacaoSerializer(serializers.ModelSerializer):
    total_pessoas = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Confirmacao
        fields = [
            'id', 'nome', 'email', 'telefone', 'presenca',
            'acompanhantes', 'mensagem', 'criado_em', 'total_pessoas',
        ]
        read_only_fields = ['id', 'criado_em', 'total_pessoas']

    def get_total_pessoas(self, confirmacao):
        return confirmacao.total_pessoas()


class PresenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Presente
        fields = ['id', 'nome', 'descricao', 'valor', 'emoji', 'ordem', 'reservado']
        read_only_fields = fields
