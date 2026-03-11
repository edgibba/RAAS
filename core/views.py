from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import SolicitacaoAcessoForm


@login_required
def dashboard(request):
    return render(request, "core/dashboard.html")


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