from django.db import models


class DebentureCadastro(models.Model):
    # Identificação
    codigo_ativo = models.CharField(max_length=20, primary_key=True)
    empresa = models.CharField(max_length=300, blank=True)
    serie = models.CharField(max_length=20, blank=True)
    emissao = models.CharField(max_length=20, blank=True)
    ipo = models.CharField(max_length=10, blank=True)
    situacao = models.CharField(max_length=50, blank=True)
    isin = models.CharField(max_length=20, blank=True)
    cnpj = models.CharField(max_length=20, blank=True)

    # Registro CVM
    registro_cvm_emissao = models.CharField(max_length=100, blank=True)
    dt_registro_cvm_emissao = models.DateField(null=True, blank=True)
    registro_cvm_programa = models.CharField(max_length=100, blank=True)
    dt_registro_cvm_programa = models.DateField(null=True, blank=True)

    # Datas
    dt_emissao = models.DateField(null=True, blank=True)
    dt_vencimento = models.DateField(null=True, blank=True)
    motivo_saida = models.CharField(max_length=100, blank=True)
    dt_saida_novo_vencimento = models.DateField(null=True, blank=True)
    dt_inicio_rentabilidade = models.DateField(null=True, blank=True)
    dt_inicio_distribuicao = models.DateField(null=True, blank=True)
    dt_proxima_repactuacao = models.DateField(null=True, blank=True)
    dt_ult_vna = models.DateField(null=True, blank=True)
    ato_societario_1 = models.CharField(max_length=20, blank=True)
    dt_ato_1 = models.DateField(null=True, blank=True)
    ato_societario_2 = models.CharField(max_length=20, blank=True)
    dt_ato_2 = models.DateField(null=True, blank=True)

    # Características
    forma = models.CharField(max_length=50, blank=True)
    garantia_especie = models.CharField(max_length=100, blank=True)
    classe = models.CharField(max_length=50, blank=True)
    artigo_14 = models.CharField(max_length=10, blank=True)
    artigo_24 = models.CharField(max_length=10, blank=True)
    tipo_amortizacao = models.CharField(max_length=100, blank=True)
    deb_incentivada = models.CharField(max_length=10, blank=True)
    escritura_padronizada = models.CharField(max_length=10, blank=True)
    resgate_antecipado = models.CharField(max_length=200, blank=True)

    # Quantidades
    qtd_emitida = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    qtd_mercado = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    qtd_tesouraria = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    qtd_resgatada = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    qtd_cancelada = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    qtd_convertida_snd = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    qtd_convertida_fora_snd = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    qtd_permutada_snd = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    qtd_permutada_fora_snd = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)

    # Valor nominal
    unidade_monetaria_emissao = models.CharField(max_length=20, blank=True)
    vn_emissao = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    unidade_monetaria_atual = models.CharField(max_length=20, blank=True)
    vn_atual = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)

    # Indexador
    indice = models.CharField(max_length=50, blank=True)
    tipo_indice = models.CharField(max_length=50, blank=True)
    criterio_calculo = models.CharField(max_length=100, blank=True)
    dia_ref_indice_precos = models.CharField(max_length=10, blank=True)
    criterio_indice = models.CharField(max_length=100, blank=True)
    corrige_a_cada = models.CharField(max_length=50, blank=True)
    pct_multiplicador = models.CharField(max_length=100, blank=True)
    limite_tjlp = models.CharField(max_length=50, blank=True)
    tipo_limite_tjlp = models.CharField(max_length=100, blank=True)
    juros_criterio_antigo = models.CharField(max_length=100, blank=True)
    premios_criterio_antigo = models.CharField(max_length=100, blank=True)

    # Amortização
    amort_taxa = models.CharField(max_length=50, blank=True)
    amort_cada = models.CharField(max_length=50, blank=True)
    amort_unidade = models.CharField(max_length=50, blank=True)
    amort_carencia = models.CharField(max_length=50, blank=True)
    amort_criterio = models.CharField(max_length=100, blank=True)

    # Juros
    juros_taxa = models.CharField(max_length=50, blank=True)
    juros_prazo = models.CharField(max_length=50, blank=True)
    juros_cada = models.CharField(max_length=50, blank=True)
    juros_unidade = models.CharField(max_length=50, blank=True)
    juros_carencia = models.CharField(max_length=50, blank=True)
    juros_criterio = models.CharField(max_length=100, blank=True)
    juros_tipo = models.CharField(max_length=50, blank=True)

    # Prêmio
    premio_taxa = models.CharField(max_length=50, blank=True)
    premio_prazo = models.CharField(max_length=50, blank=True)
    premio_cada = models.CharField(max_length=50, blank=True)
    premio_unidade = models.CharField(max_length=50, blank=True)
    premio_carencia = models.CharField(max_length=50, blank=True)
    premio_criterio = models.CharField(max_length=100, blank=True)
    premio_tipo = models.CharField(max_length=50, blank=True)

    # Participação
    participacao_taxa = models.CharField(max_length=50, blank=True)
    participacao_cada = models.CharField(max_length=50, blank=True)
    participacao_unidade = models.CharField(max_length=50, blank=True)
    participacao_carencia = models.CharField(max_length=50, blank=True)
    participacao_descricao = models.CharField(max_length=200, blank=True)

    # Agentes
    banco_mandatario = models.CharField(max_length=200, blank=True)
    agente_fiduciario = models.CharField(max_length=200, blank=True)
    instituicao_depositaria = models.CharField(max_length=200, blank=True)
    coordenador_lider = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = "DebentureCadastro"

    def __str__(self):
        return f"{self.codigo_ativo} - {self.empresa}"


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