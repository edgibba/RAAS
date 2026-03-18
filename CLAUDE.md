# Projeto Accrual

## Visão geral
Aplicação web Django para cálculo de **VNA (Valor Nominal Atualizado)** de títulos de renda fixa corrigidos por índices de preços (ex: IPCA). Replica a lógica de planilhas financeiras com precisão de 8 a 16 casas decimais.

## Stack
- **Backend:** Django 6.0.3, Python
- **Banco:** PostgreSQL (psycopg3) — `db.sqlite3` existe mas é apenas dev local
- **Servidor:** Gunicorn + Whitenoise (produção)
- **Autenticação:** `login_required` + solicitação de acesso com aprovação manual

## Estrutura principal

```
E:/accrual_project/
├── core/
│   ├── models.py                  # SolicitacaoAcesso (fluxo de cadastro de usuários)
│   ├── views.py                   # dashboard, calculadora_vna_view, solicitar_acesso
│   ├── forms.py
│   ├── management/commands/
│   │   └── carga_base_vna.py      # Comando de carga de dados (CSV → banco)
│   └── services/vna/
│       ├── vna.py                 # Lógica principal de cálculo do VNA
│       ├── calendario.py          # Contagem de dias úteis, aniversários ajustados
│       ├── indices.py             # Consulta de NI mensais (real ou projetado)
│       ├── modelos.py             # Dataclasses: ResultadoVNA, EtapaAuditoriaVNA, etc.
│       ├── exceptions.py          # Hierarquia de exceções do domínio
│       ├── db.py                  # Context manager de conexão psycopg
│       ├── auditoria.py
│       └── logger_config.py
├── data/
│   ├── calendario.csv             # Dias úteis (dtBase, bUtil)
│   └── indices_mensais.csv        # Série histórica de NI (IPCA etc.)
└── db.sqlite3
```

## Tabelas do banco (raw SQL, sem ORM Django)

| Tabela | Descrição |
|--------|-----------|
| `Calendario` | Dias do calendário com flag `bUtil` (dia útil). PK: `dtBase` |
| `Indices` | Cadastro de índices (ex: IPCA). PK: `idIndice`, unique: `nome` |
| `IndicesMensaisTempo` | Série mensal de NI. PK composta: `(idIndice, nAno, nMes, bReal)` |

> As tabelas são acessadas via `cursor.execute` diretamente — não são models Django.

## Carga de dados

```bash
# Ativa o ambiente virtual primeiro
.venv\Scripts\activate

# Recarregar apenas o calendário (apaga e recarrega)
python manage.py carga_base_vna --apenas-calendario --limpar

# Recarregar apenas os índices (apaga e recarrega)
python manage.py carga_base_vna --apenas-indices --limpar

# Carregar tudo
python manage.py carga_base_vna --limpar

# Validar sem gravar
python manage.py carga_base_vna --dry-run
```

A carga usa `executemany` em lotes de 500 linhas com `ON CONFLICT DO UPDATE`.

## Lógica de cálculo do VNA

- **Entrada:** `id_indice`, `data_inicio_rentabilidade`, `data_vna`, `vne=1000`, `dia_referencia=15`
- **Pro-rata:** somente `DU` (dias úteis) implementado
- **Tipos de período:** Integral, Parcial inicial, Parcial final, Parcial único
- **Precisão:** fator mensal truncado em 8 casas; fator acumulado truncado em 16 casas
- **NI:** usa valor real quando `dtDivulgacao <= data_vna`; caso contrário usa projetado

## Comandos úteis

```bash
.venv\Scripts\activate          # ativa ambiente virtual
python manage.py runserver      # sobe servidor local
python manage.py shell          # shell interativo Django
```
