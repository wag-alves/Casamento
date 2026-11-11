from django import forms
from .models import Confirmacao


class ConfirmacaoForm(forms.ModelForm):
    class Meta:
        model = Confirmacao
        fields = ['nome', 'email', 'telefone', 'presenca', 'acompanhantes', 'mensagem']
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Seu nome completo', 'class': 'form-control', 'required': True
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'seuemail@exemplo.com', 'class': 'form-control'
            }),
            'telefone': forms.TextInput(attrs={
                'placeholder': '(84) 90000-0000', 'class': 'form-control'
            }),
            'presenca': forms.RadioSelect(),
            'acompanhantes': forms.Textarea(attrs={
                'placeholder': 'Ex:\nMaria da Silva\nJoão Souza',
                'class': 'form-control',
                'rows': 4,
            }),
            'mensagem': forms.Textarea(attrs={
                'placeholder': 'Deixe um recado para os noivos (opcional)',
                'class': 'form-control',
                'rows': 3,
            }),
        }
        labels = {
            'acompanhantes': 'Vai levar acompanhante(s)? Liste os nomes abaixo',
        }


class ReservaPresenteForm(forms.Form):
    nome = forms.CharField(
        label='Seu nome',
        max_length=200,
        widget=forms.TextInput(attrs={
            'placeholder': 'Seu nome completo', 'class': 'form-control', 'required': True
        }),
    )
    mensagem = forms.CharField(
        label='Mensagem para os noivos (opcional)',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Deixe um recado (opcional)', 'class': 'form-control', 'rows': 3
        }),
    )
