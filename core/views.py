import json
from decimal import Decimal
from pathlib import Path
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.shortcuts import render, redirect
from django_ratelimit.decorators import ratelimit
from .forms import CalculadoraVNAForm, SolicitacaoAcessoForm
from .models import DebentureCadastro, DebentureFluxo
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


@login_required
def fluxo_debenture_view(request, codigo):
    try:
        debenture = DebentureCadastro.objects.get(codigo_ativo__iexact=codigo)
    except DebentureCadastro.DoesNotExist:
        debenture = None

    fluxos = (
        DebentureFluxo.objects.filter(cod_deb_id=codigo.upper().strip())
        .order_by("dt_evento", "evento")
    )

    return render(
        request,
        "core/fluxo_debenture.html",
        {
            "debenture": debenture,
            "codigo": codigo.upper(),
            "fluxos": fluxos,
        },
    )


@login_required
def autocomplete_debenture(request):
    from django.http import JsonResponse
    q = request.GET.get("q", "").strip().upper()
    if len(q) < 2:
        return JsonResponse([], safe=False)
    qs = (
        DebentureCadastro.objects
        .filter(codigo_ativo__istartswith=q)
        .values("codigo_ativo", "empresa")
        .order_by("codigo_ativo")[:20]
    )
    return JsonResponse(
        [{"codigo": r["codigo_ativo"], "empresa": r["empresa"]} for r in qs],
        safe=False,
    )


@login_required
def consulta_debenture_view(request):
    codigo = request.GET.get("codigo", "").strip().upper()
    debenture = None
    erro = None

    if codigo:
        try:
            debenture = DebentureCadastro.objects.get(codigo_ativo__iexact=codigo)
        except DebentureCadastro.DoesNotExist:
            erro = f"Debênture '{codigo}' não encontrada."

    return render(
        request,
        "core/consulta_debenture.html",
        {
            "codigo": codigo,
            "debenture": debenture,
            "erro": erro,
        },
    )