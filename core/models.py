from django.db import models


class SolicitacaoAcesso(models.Model):
    STATUS_CHOICES = [
        ("PENDENTE", "Pendente"),
        ("APROVADA", "Aprovada"),
        ("REJEITADA", "Rejeitada"),
    ]

    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    empresa = models.CharField(max_length=200)
    nickname = models.CharField(max_length=150, unique=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDENTE",
    )

    observacao_admin = models.TextField(blank=True, null=True)

    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_decisao = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.nickname} - {self.nome} ({self.status})"