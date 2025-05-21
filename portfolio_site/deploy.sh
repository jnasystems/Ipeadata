#!/bin/bash

set -e

echo "🔧 Gerando build com npm run build..."
npm run build

# Cria build temporária fora do Git
TMP_DIR="$(mktemp -d)"
cp -r dist/* "$TMP_DIR"

CURRENT_BRANCH=$(git branch --show-current)

echo "🔄 Mudando para a branch 'page'..."
git checkout page

echo "🧹 Limpando arquivos antigos..."
find . -mindepth 1 ! -regex '^./\.git\(/.*\)?' -delete

echo "📦 Copiando arquivos da build para a raiz da branch 'page'..."
cp -r "$TMP_DIR"/* .

echo "🧽 Limpando build temporária..."
rm -rf "$TMP_DIR"

echo "📤 Commitando e enviando..."
git add .
git commit -m "Deploy automático"
git push origin page

echo "↩️ Voltando para '$CURRENT_BRANCH'..."
git checkout "$CURRENT_BRANCH"

echo "✅ Deploy finalizado com sucesso!"
