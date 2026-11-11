from django.urls import path
from . import views, api_views

urlpatterns = [
    path('api/health/', api_views.HealthCheckAPIView.as_view(), name='api_health'),
    path('api/presentes/', api_views.ListaPresentesAPIView.as_view(), name='api_presentes'),
    path('api/confirmacoes/', api_views.ConfirmacoesAPIView.as_view(), name='api_confirmacoes'),
    path('api/confirmacoes/<int:pk>/', api_views.ConfirmacaoDetalheAPIView.as_view(), name='api_confirmacao_detalhe'),
    path('', views.home, name='home'),
    path('obrigado/', views.obrigado, name='obrigado'),

    path('presentes/', views.presentes, name='presentes'),
    path('presentes/<int:pk>/', views.presente_detail, name='presente_detail'),
    path('presentes/<int:pk>/qrcode.png', views.presente_qrcode, name='presente_qrcode'),
    path('presentes/obrigado/', views.presente_obrigado, name='presente_obrigado'),
]
