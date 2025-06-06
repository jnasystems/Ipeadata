#!/bin/bash

set -e

# Vai para a pasta onde está o script
cd "$(dirname "$0")"

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

if git commit -m "Deploy automático para GitHub Pages"; then
  echo "✅ Commit realizado."
else
  echo "ℹ️ Nenhuma mudança detectada para commit. Forçando push mesmo assim..."
fi

# Push forçado para garantir deploy
echo "🚀 Enviando para GitHub Pages com --force..."
git push origin page --force

echo "🔁 Voltando para a branch '$CURRENT_BRANCH'..."
git checkout "$CURRENT_BRANCH"
cd "$PROJECT_ROOT"

echo "🎉 Deploy finalizado com sucesso!"

# Comando para dar permissão de execução ao script
# chmod +x deploy.sh