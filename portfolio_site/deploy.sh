#!/bin/bash

set -e

echo "🔧 Entrando na pasta do projeto Vite..."
cd portfolio_site

echo "📦 Gerando build com npm run build..."
npm run build

# Salva a pasta onde o build foi feito
BUILD_DIR="$(pwd)/dist"

echo "⬅️ Voltando para a raiz do repositório..."
cd ..

CURRENT_BRANCH=$(git branch --show-current)

echo "🔄 Mudando para a branch 'page'..."
git checkout page

echo "🧹 Limpando arquivos antigos..."
find . -mindepth 1 ! -regex '^./\.git\(/.*\)?' -delete

echo "📂 Copiando arquivos da build para a raiz da branch..."
cp -r "$BUILD_DIR/"* .

echo "📤 Commitando e enviando para o GitHub..."
git add .
git commit -m "Deploy automático para GitHub Pages"
git push origin page

echo "↩️ Voltando para a branch '$CURRENT_BRANCH'..."
git checkout "$CURRENT_BRANCH"

echo "✅ Deploy finalizado com sucesso!"
