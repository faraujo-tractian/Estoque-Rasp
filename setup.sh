#!/bin/bash

# Setup script for Sistema de Controle de Estoque 5S
# Run this on your Raspberry Pi or Linux machine

echo "🚀 Instalando Sistema de Controle de Estoque 5S..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instalando..."
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
fi

# Create virtual environment
echo "📦 Criando ambiente virtual..."
cd backend
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Instalando dependências..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Criando diretórios..."
mkdir -p ../data
mkdir -p ../credentials

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚙️  Criando arquivo .env..."
    cp .env.example .env
    echo "⚠️  ATENÇÃO: Edite o arquivo backend/.env com suas credenciais!"
fi

echo ""
echo "✅ Instalação concluída!"
echo ""
echo "📝 Próximos passos:"
echo "1. Coloque suas credenciais do Google Sheets em: credentials/google_sheets_key.json"
echo "2. Edite o arquivo backend/.env com suas configurações"
echo "3. Execute: cd backend && source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo ""
echo "🌐 Acesse: http://localhost:8000"
echo ""

