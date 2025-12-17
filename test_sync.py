"""
Teste de sincronização com Google Sheets
"""
import sys
import os
from dotenv import load_dotenv

# Carregar .env manualmente
env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
load_dotenv(env_path)

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from app.services.google_sheets import GoogleSheetsService

async def test():
    print("=" * 80)
    print("TESTE DE SINCRONIZAÇÃO COM GOOGLE SHEETS")
    print("=" * 80)
    
    try:
        print("\n1. Criando serviço...")
        service = GoogleSheetsService()
        
        print("2. Conectando...")
        service.connect()
        print(f"✅ Conectado à planilha: {service.spreadsheet.title}")
        
        print("\n3. Listando abas disponíveis:")
        for i, sheet_name in enumerate(service.spreadsheet.worksheets(), 1):
            print(f"   {i}. {sheet_name.title}")
        
        print("\n4. Iniciando sincronização...")
        result = await service.sync_from_sheets()
        
        print("\n" + "=" * 80)
        print("RESULTADO:")
        print("=" * 80)
        for key, value in result.items():
            print(f"  {key}: {value}")
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())

