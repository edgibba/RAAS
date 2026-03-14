#!/usr/bin/env bash
set -o errexit

echo "Instalando dependencias..."
pip install -r requirements.txt

echo "Executando migrations..."
python manage.py migrate --noinput

echo "Coletando arquivos static..."
python manage.py collectstatic --noinput

echo "Build finalizado com sucesso."