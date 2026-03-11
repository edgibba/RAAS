from django import forms
from .models import SolicitacaoAcesso


class SolicitacaoAcessoForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoAcesso
        fields = ["nome", "email", "empresa", "nickname"]
        labels = {
            "nome": "Nome completo",
            "email": "E-mail",
            "empresa": "Empresa",
            "nickname": "Login desejado",
        }
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "Informe seu nome completo"}),
            "email": forms.EmailInput(attrs={"placeholder": "Informe seu e-mail"}),
            "empresa": forms.TextInput(attrs={"placeholder": "Informe sua empresa"}),
            "nickname": forms.TextInput(attrs={"placeholder": "Escolha um login"}),
        }

    def clean_nickname(self):
        nickname = self.cleaned_data["nickname"].strip().lower()
        return nickname

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        return email