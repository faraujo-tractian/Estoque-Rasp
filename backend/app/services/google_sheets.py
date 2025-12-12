"""
Google Sheets Service
Handles synchronization with Google Sheets using service account
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any
from datetime import datetime
from app.config import settings
from app.services.database import Database
from app.models.item import Item
import os


class GoogleSheetsService:
    """Google Sheets integration service"""
    
    # Required scopes for Google Sheets API
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    def __init__(self):
        self.spreadsheet_id = settings.GOOGLE_SHEETS_SPREADSHEET_ID
        self.credentials_file = settings.GOOGLE_SHEETS_CREDENTIALS_FILE
        self.db = Database()
        self.client = None
        self.spreadsheet = None
    
    def connect(self):
        """Connect to Google Sheets"""
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Arquivo de credenciais não encontrado: {self.credentials_file}"
            )
        
        if not self.spreadsheet_id:
            raise ValueError("GOOGLE_SHEETS_SPREADSHEET_ID não configurado")
        
        # Authenticate
        creds = Credentials.from_service_account_file(
            self.credentials_file,
            scopes=self.SCOPES
        )
        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
    
    async def sync_from_sheets(self):
        """Sync items from Google Sheets to local database"""
        try:
            self.connect()
            
            # Get ITENS worksheet
            try:
                items_sheet = self.spreadsheet.worksheet("ITENS")
            except gspread.WorksheetNotFound:
                items_sheet = self.spreadsheet.sheet1  # Fallback to first sheet
            
            # Get all records (assumes header row)
            records = items_sheet.get_all_records()
            
            # Sync each item
            for record in records:
                item = Item(
                    id=record.get('ID'),
                    nome=record.get('Item') or record.get('Nome') or record.get('item'),
                    categoria=record.get('Categoria') or record.get('categoria'),
                    quantidade_disponivel=int(record.get('Qtd_Disponível') or record.get('Quantidade') or 0),
                    estoque_minimo=int(record.get('Estoque_Mínimo') or record.get('Minimo') or 0),
                    localizacao=record.get('Localização') or record.get('Localizacao')
                )
                
                if item.nome:  # Only sync if item has a name
                    self.db.upsert_item(item)
            
            print(f"✅ Sincronizados {len(records)} itens do Google Sheets")
            return {"success": True, "items_synced": len(records)}
            
        except Exception as e:
            print(f"❌ Erro ao sincronizar com Google Sheets: {e}")
            raise
    
    async def update_item_quantity(self, item_name: str, new_quantity: int):
        """Update item quantity in Google Sheets"""
        try:
            self.connect()
            
            items_sheet = self.spreadsheet.worksheet("ITENS")
            
            # Find the item row
            cell = items_sheet.find(item_name)
            if cell:
                # Update the quantity column (assuming it's in column D or similar)
                # You may need to adjust the column based on your sheet structure
                items_sheet.update_cell(cell.row, 4, new_quantity)  # Column 4 = D
                
        except Exception as e:
            print(f"⚠️  Erro ao atualizar quantidade no Sheets: {e}")
    
    async def append_to_history(self, transaction: Dict[str, Any]):
        """Append transaction to HISTÓRICO worksheet"""
        try:
            self.connect()
            
            # Get or create HISTÓRICO worksheet
            try:
                history_sheet = self.spreadsheet.worksheet("HISTÓRICO")
            except gspread.WorksheetNotFound:
                history_sheet = self.spreadsheet.add_worksheet(
                    title="HISTÓRICO",
                    rows=1000,
                    cols=10
                )
                # Add headers
                history_sheet.append_row([
                    "Data/Hora", "Tipo", "Item", "Quantidade", 
                    "Usuário", "Saldo Após", "Observações"
                ])
            
            # Append transaction
            row = [
                transaction.get('timestamp', datetime.now().isoformat()),
                transaction.get('tipo', '').upper(),
                transaction.get('item_nome', ''),
                transaction.get('quantidade', 0),
                transaction.get('nome_pessoa', ''),
                transaction.get('saldo_apos', 0),
                ''  # Observações
            ]
            
            history_sheet.append_row(row)
            
        except Exception as e:
            print(f"⚠️  Erro ao adicionar ao histórico: {e}")
    
    def get_slack_user_mapping(self) -> Dict[str, str]:
        """Get name to Slack username mapping from PESSOAS worksheet"""
        try:
            self.connect()
            
            try:
                people_sheet = self.spreadsheet.worksheet("PESSOAS")
                records = people_sheet.get_all_records()
                
                # Create mapping: nome -> slack_username
                mapping = {}
                for record in records:
                    nome = record.get('Nome', '').strip().lower()
                    slack_user = record.get('Slack_Username', '') or record.get('Slack_User_ID', '')
                    if nome and slack_user:
                        mapping[nome] = slack_user
                
                return mapping
                
            except gspread.WorksheetNotFound:
                print("⚠️  Worksheet PESSOAS não encontrada")
                return {}
                
        except Exception as e:
            print(f"⚠️  Erro ao buscar mapeamento de usuários: {e}")
            return {}

