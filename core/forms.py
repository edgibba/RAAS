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

        
class CalculadoraVNAForm(forms.Form):
    indice = forms.ChoiceField(
        label="Índice",
        choices=[],
        required=True,
    )
    data_inicio_rentabilidade = forms.DateField(
        label="Data início da rentabilidade",
        input_formats=["%d/%m/%Y", "%Y-%m-%d"],
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={"placeholder": "dd/mm/aaaa"},
        ),
        required=True,
    )
    data_vna = forms.DateField(
        label="Data do VNA desejado",
        input_formats=["%d/%m/%Y", "%Y-%m-%d"],
        widget=forms.DateInput(
            format="%d/%m/%Y",
            attrs={"placeholder": "dd/mm/aaaa"},
        ),
        required=True,
    )
    detalhar = forms.BooleanField(
        label="Exibir memória de cálculo auditável",
        required=False,
        initial=True,
    )

    def __init__(self, *args, indices_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["indice"].choices = indices_choices or []

    def clean(self):
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get("data_inicio_rentabilidade")
        data_vna = cleaned_data.get("data_vna")

        if data_inicio and data_vna:
            if data_vna <= data_inicio:
                raise forms.ValidationError(
                    "A data do VNA deve ser posterior à data de início da rentabilidade."
                )

        return cleaned_data