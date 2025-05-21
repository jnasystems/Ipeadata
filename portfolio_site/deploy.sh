#!/bin/bash

set -e

echo "🔧 Gerando build com npm run build..."
npm run build

# Caminho absoluto do diretório do script
SCRIPT_DIR=$(pwd)

# Cria diretório temporário fora do projeto Git
TMP_DIR="$(mktemp -d)"

# Copia apenas o conteúdo de 'portfolio_site' para o diretório temporário
cp -r "$SCRIPT_DIR/portfolio_site/"* "$TMP_DIR"

CURRENT_BRANCH=$(git branch --show-current)

echo "🔄 Mudando para a branch 'page'..."
git checkout page

echo "🧹 Limpando arquivos antigos..."
find . -mindepth 1 ! -regex '^./\.git\(/.*\)?' -delete

echo "📦 Copiando arquivos direto para a raiz da branch..."
cp -r "$TMP_DIR"/* .

echo "🧽 Removendo build temporária..."
rm -rf "$TMP_DIR"

echo "📤 Commitando e enviando para o GitHub..."
git add .
git commit -m "Deploy automático sem subpasta"
git push origin page

echo "↩️ Voltando para a branch '$CURRENT_BRANCH'..."
git checkout "$CURRENT_BRANCH"

echo "✅ Deploy finalizado com sucesso!"
