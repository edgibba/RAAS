from django.contrib import admin
from .models import SolicitacaoAcesso


@admin.register(SolicitacaoAcesso)
class SolicitacaoAcessoAdmin(admin.ModelAdmin):
    list_display = (
        "nickname",
        "nome",
        "email",
        "empresa",
        "status",
        "data_solicitacao",
        "data_decisao",
    )
    list_filter = ("status", "empresa", "data_solicitacao", "data_decisao")
    search_fields = ("nickname", "nome", "email", "empresa")
    readonly_fields = ("data_solicitacao", "data_decisao")
    ordering = ("status", "-data_solicitacao")
    list_per_page = 20