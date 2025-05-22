#!/bin/bash

set -e

PROJECT_DIR_NAME="portfolio_site"

echo "📦 Instalando dependências com npm install..."
npm install

echo "🔧 Gerando build com npm run build..."
npm run build

# Caminho absoluto onde está o script
PROJECT_ROOT=$(pwd)

# Cria build temporária fora do projeto
TMP_DIR=$(mktemp -d)
cp -r "$PROJECT_ROOT/dist/"* "$TMP_DIR"

CURRENT_BRANCH=$(git branch --show-current)

echo "🔄 Mudando para a branch 'page'..."
cd "$PROJECT_ROOT/.."
git checkout page

echo "🧹 Limpando arquivos antigos da branch page..."
find . -mindepth 1 ! -regex '^./\.git\(/.*\)?' -delete

echo "📦 Copiando build direto para raiz da branch page..."
cp -r "$TMP_DIR"/* .

echo "🧽 Limpando build temporária..."
rm -rf "$TMP_DIR"

git add .

# Tenta fazer commit — mas ignora erro se nada mudou
if git commit -m "Deploy automático sem subpasta"; then
  echo "✅ Commit realizado."
else
  echo "ℹ️ Nenhuma mudança detectada para commit. Forçando push mesmo assim..."
fi

# Push sempre (útil caso algo tenha sido sobrescrito mas sem hash novo)
git push origin page


echo "↩️ Voltando para a branch '$CURRENT_BRANCH'..."
git checkout "$CURRENT_BRANCH"
cd "$PROJECT_ROOT"

echo "✅ Deploy finalizado com sucesso!"
