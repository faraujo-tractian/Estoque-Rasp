"""
Script de teste para verificar configuração
Execute: python test_setup.py
"""

import os
import sys
from pathlib import Path

def check_file(path, description):
    """Check if file exists"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {path}")
    return exists

def check_env_var(var_name):
    """Check if environment variable is set"""
    value = os.getenv(var_name)
    is_set = bool(value and value.strip())
    status = "✅" if is_set else "⚠️ "
    print(f"{status} {var_name}: {'Configurado' if is_set else 'NÃO configurado'}")
    return is_set

print("🔍 Verificando configuração do Sistema de Estoque...\n")

print("=" * 60)
print("ESTRUTURA DE ARQUIVOS")
print("=" * 60)

# Check project structure
checks = [
    ("backend/app/main.py", "Backend principal"),
    ("backend/requirements.txt", "Dependências"),
    ("frontend/index.html", "Frontend"),
    ("credentials/google_sheets_key.json", "Credenciais Google Sheets"),
    ("backend/.env", "Arquivo de configuração"),
]

all_files_ok = all(check_file(path, desc) for path, desc in checks)

print("\n" + "=" * 60)
print("VARIÁVEIS DE AMBIENTE (backend/.env)")
print("=" * 60)

# Load .env if exists
env_path = Path("backend/.env")
if env_path.exists():
    from dotenv import load_dotenv
    load_dotenv(env_path)
    
    env_vars = [
        "GOOGLE_SHEETS_SPREADSHEET_ID",
        "SLACK_BOT_TOKEN",
        "SLACK_CHANNEL",
    ]
    
    all_env_ok = all(check_env_var(var) for var in env_vars)
else:
    print("❌ Arquivo .env não encontrado!")
    all_env_ok = False

print("\n" + "=" * 60)
print("DEPENDÊNCIAS PYTHON")
print("=" * 60)

try:
    import fastapi
    print("✅ FastAPI instalado")
except ImportError:
    print("❌ FastAPI NÃO instalado")

try:
    import gspread
    print("✅ gspread instalado")
except ImportError:
    print("❌ gspread NÃO instalado")

try:
    import slack_sdk
    print("✅ slack-sdk instalado")
except ImportError:
    print("❌ slack-sdk NÃO instalado")

try:
    from pydantic_settings import BaseSettings
    print("✅ pydantic-settings instalado")
except ImportError:
    print("❌ pydantic-settings NÃO instalado")

print("\n" + "=" * 60)
print("RESUMO")
print("=" * 60)

if all_files_ok and all_env_ok:
    print("✅ Sistema configurado corretamente!")
    print("\n🚀 Para iniciar o servidor, execute:")
    print("   cd backend")
    print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000")
else:
    print("⚠️  Configuração incompleta. Verifique os itens acima.")
    print("\n📝 Próximos passos:")
    if not check_file("credentials/google_sheets_key.json", ""):
        print("   1. Adicione google_sheets_key.json em credentials/")
    if not all_env_ok:
        print("   2. Configure as variáveis no arquivo backend/.env")
    print("   3. Instale as dependências: pip install -r backend/requirements.txt")

