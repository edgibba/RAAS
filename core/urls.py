from django.urls import path
from .views import (
    dashboard,
    solicitar_acesso,
    solicitacao_acesso_sucesso,
)

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("solicitar-acesso/", solicitar_acesso, name="solicitar_acesso"),
    path(
        "solicitacao-acesso-sucesso/",
        solicitacao_acesso_sucesso,
        name="solicitacao_acesso_sucesso",
    ),
]