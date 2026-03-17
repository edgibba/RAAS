#!/usr/bin/env bash
set -o errexit

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Gerando informacoes de versao..."
cat > version.json << EOF
{
  "commit": "$(git rev-parse HEAD)",
  "commit_short": "$(git rev-parse --short HEAD)",
  "branch": "$(git rev-parse --abbrev-ref HEAD)",
  "build_at": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF

echo "Executando migrations..."
python manage.py migrate --noinput

echo "Coletando arquivos static..."
python manage.py collectstatic --noinput

echo "Build finalizado com sucesso."