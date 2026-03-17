import json
from decimal import Decimal
from pathlib import Path
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import render, redirect
from django_ratelimit.decorators import ratelimit
from .forms import CalculadoraVNAForm, SolicitacaoAcessoForm
from core.services.vna.indices import listar_indices_mensais
from core.services.vna.vna import calcular_vna


@login_required
def dashboard(request):
    return render(request, "core/dashboard.html")


@ratelimit(key="ip", rate="5/h", method="POST", block=True)
def solicitar_acesso(request):
    if request.method == "POST":
        form = SolicitacaoAcessoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("solicitacao_acesso_sucesso")
    else:
        form = SolicitacaoAcessoForm()

    return render(
        request,
        "core/solicitar_acesso.html",
        {"form": form},
    )


def solicitacao_acesso_sucesso(request):
    return render(request, "core/solicitacao_acesso_sucesso.html")


@login_required
def about(request):
    version_path = Path(settings.BASE_DIR) / "version.json"
    try:
        version = json.loads(version_path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        version = None
    return render(request, "core/about.html", {"version": version})
    
@login_required
def calculadora_vna_view(request):
    indices = listar_indices_mensais(connection)
    indices_choices = [(str(i.id_indice), i.nome) for i in indices]

    resultado = None
    erro = None

    if request.method == "POST":
        form = CalculadoraVNAForm(request.POST, indices_choices=indices_choices)
        if form.is_valid():
            try:
                id_indice = int(form.cleaned_data["indice"])
                data_inicio = form.cleaned_data["data_inicio_rentabilidade"]
                data_vna = form.cleaned_data["data_vna"]
                dia_ref = form.cleaned_data["dia_referencia"]
                detalhar = form.cleaned_data["detalhar"]

                resultado = calcular_vna(
                    conn=connection,
                    id_indice=id_indice,
                    data_inicio_rentabilidade=data_inicio,
                    data_vna=data_vna,
                    vne=Decimal("1000"),
                    base_pro_rata="DU",
                    dia_referencia=dia_ref,
                    detalhar=detalhar,
                )
            except Exception as exc:
                erro = str(exc)
    else:
        form = CalculadoraVNAForm(indices_choices=indices_choices)

    return render(
        request,
        "core/calculadora_vna.html",
        {
            "form": form,
            "resultado": resultado,
            "erro": erro,
        },
    )    