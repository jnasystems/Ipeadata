#!/bin/bash

set -e

echo "🔧 Gerando build com npm run build..."
npm run build

# Caminho absoluto temporário (fora do repositório)
TMP_DIR="/tmp/deploy_tmp_$(date +%s)"
mkdir -p "$TMP_DIR"
cp -r dist/* "$TMP_DIR"

CURRENT_BRANCH=$(git branch --show-current)

echo "🔄 Mudando para a branch 'page'..."
git checkout page

echo "🧹 Limpando arquivos antigos..."
find . -mindepth 1 ! -regex '^./\.git\(/.*\)?' -delete

echo "📦 Copiando arquivos da build temporária para a raiz da branch 'page'..."
cp -r "$TMP_DIR"/* .

echo "🧽 Limpando build temporário..."
rm -rf "$TMP_DIR"

echo "📤 Commitando e enviando..."
git add .
git commit -m "Deploy automático"
git push origin page

echo "↩️ Voltando para '$CURRENT_BRANCH'..."
git checkout "$CURRENT_BRANCH"

echo "✅ Deploy finalizado com sucesso!"
