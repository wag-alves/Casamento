from django.db import connection
from django.db.utils import OperationalError
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ConfirmacaoSerializer, PresenteSerializer
from .models import Confirmacao, Presente
from .views import _enviar_email_confirmacao


class HealthCheckAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                cursor.fetchone()
        except OperationalError:
            return Response({'status': 'unhealthy', 'database': 'unavailable'}, status=503)
        return Response({'status': 'ok', 'database': 'ok'})


class ListaPresentesAPIView(generics.ListAPIView):
    serializer_class = PresenteSerializer
    queryset = Presente.objects.all().order_by('reservado', 'ordem', 'nome')


class ConfirmacoesAPIView(generics.ListCreateAPIView):
    """POST é público (convidados confirmam presença); GET lista só para administradores,
    porque a resposta contém nome, e-mail e telefone dos convidados."""
    serializer_class = ConfirmacaoSerializer
    queryset = Confirmacao.objects.all()
    authentication_classes = [SessionAuthentication]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAdminUser()]

    def perform_create(self, serializer):
        confirmacao = serializer.save()
        _enviar_email_confirmacao(confirmacao)


class ConfirmacaoDetalheAPIView(generics.RetrieveDestroyAPIView):
    """GET e DELETE de uma confirmação — somente administradores (sessão do /admin/)."""
    serializer_class = ConfirmacaoSerializer
    queryset = Confirmacao.objects.all()
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]
