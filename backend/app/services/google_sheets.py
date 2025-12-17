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
        """
        Sync items from Google Sheets to local database
        Agrega itens por nome (5S individual → estoque consolidado)
        """
        try:
            self.connect()
            
            all_items = []
            total_records = 0
            
            # Ler todas as 3 abas
            for aba_nome in ["Produto", "Mecânica", "Eletrônica"]:
                try:
                    sheet = self.spreadsheet.worksheet(aba_nome)
                    records = sheet.get_all_records()
                    
                    for record in records:
                        # Pegar nome do item (pode variar o nome da coluna)
                        nome = (record.get('Nome_do_Recurso') or 
                               record.get('Nome') or 
                               record.get('Item') or 
                               record.get('nome'))
                        
                        if not nome or str(nome).strip() == '':
                            continue  # Pula linhas vazias
                        
                        all_items.append({
                            'nome': str(nome).strip(),
                            'codigo': record.get('ID_do_Recurso') or record.get('ID'),
                            'categoria': record.get('Categoria'),
                            'localizacao': record.get('Localizacao_de_armazenamento') or record.get('Localização'),
                            'aba_origem': aba_nome
                        })
                        total_records += 1
                    
                    print(f"Lidos {len(records)} registros da aba '{aba_nome}'")
                    
                except gspread.WorksheetNotFound:
                    print(f"Aba '{aba_nome}' nao encontrada, pulando...")
                    continue
            
            if not all_items:
                print("Nenhum item encontrado nas planilhas")
                return {"success": False, "error": "Nenhum item encontrado"}
            
            # Agrupar itens por (nome, aba_origem)
            # Importante: um item pode aparecer em várias abas!
            items_agrupados = {}
            for item in all_items:
                nome = item['nome']
                aba = item['aba_origem']
                chave = f"{nome}|{aba}"  # Chave única: nome + aba
                if chave not in items_agrupados:
                    items_agrupados[chave] = []
                items_agrupados[chave].append(item)
            
            # Sincronizar itens agrupados
            items_novos = 0
            items_atualizados = 0
            
            for chave, grupo in items_agrupados.items():
                # Extrair nome e aba da chave
                nome_chave, aba_origem = chave.split('|')
                
                quantidade_total = len(grupo)
                codigos = [item['codigo'] for item in grupo if item.get('codigo')]
                
                # Pega dados do primeiro (todos deveriam ter mesmos dados)
                primeiro = grupo[0]
                nome = primeiro.get('nome')  # Nome real do item (sem a chave)
                categoria = primeiro.get('categoria')
                localizacao = primeiro.get('localizacao')
                
                # DEBUG: Log para os primeiros itens
                if items_novos + items_atualizados < 3:
                    print(f"DEBUG: Item '{nome}' -> aba_origem='{aba_origem}' (grupo de {len(grupo)} unidades)")
                
                # Busca item existente no banco (considerando nome E aba)
                item_existente = self.db.get_item_by_name_and_aba(nome, aba_origem)
                
                if item_existente:
                    # Verifica se quantidade mudou (itens novos adicionados)
                    if item_existente['quantidade_total'] != quantidade_total:
                        diferenca = quantidade_total - item_existente['quantidade_total']
                        
                        # Atualiza quantidades
                        item_data = {
                            'nome': nome,
                            'categoria': categoria,
                            'localizacao': localizacao,
                            'quantidade_total': quantidade_total,
                            'quantidade_disponivel': item_existente['quantidade_disponivel'] + diferenca,
                            'quantidade_em_uso': item_existente['quantidade_em_uso'],
                            'estoque_minimo': item_existente.get('estoque_minimo', 2),
                            'codigos_originais': ','.join(codigos),
                            'aba_origem': aba_origem
                        }
                        
                        self.db.upsert_item(item_data)
                        items_atualizados += 1
                        
                        if diferenca > 0:
                            print(f"+{diferenca} unidade(s) de '{nome}'")
                    else:
                        # Atualiza metadados mesmo sem mudança de quantidade
                        # (importante para corrigir aba_origem)
                        if item_existente.get('aba_origem') != aba_origem:
                            item_data = {
                                'nome': nome,
                                'categoria': categoria,
                                'localizacao': localizacao,
                                'quantidade_total': quantidade_total,
                                'quantidade_disponivel': item_existente['quantidade_disponivel'],
                                'quantidade_em_uso': item_existente['quantidade_em_uso'],
                                'estoque_minimo': item_existente.get('estoque_minimo', 2),
                                'codigos_originais': ','.join(codigos),
                                'aba_origem': aba_origem
                            }
                            self.db.upsert_item(item_data)
                            items_atualizados += 1
                            print(f"Atualizado setor de '{nome}': {item_existente.get('aba_origem')} -> {aba_origem}")
                else:
                    # Criar novo item
                    item_data = {
                        'nome': nome,
                        'categoria': categoria,
                        'localizacao': localizacao,
                        'quantidade_total': quantidade_total,
                        'quantidade_disponivel': quantidade_total,  # Tudo disponível inicialmente
                        'quantidade_em_uso': 0,
                        'estoque_minimo': max(2, int(quantidade_total * 0.2)),  # 20% ou mínimo 2
                        'codigos_originais': ','.join(codigos),
                        'aba_origem': aba_origem
                    }
                    
                    self.db.upsert_item(item_data)
                    items_novos += 1
                    print(f"Novo item: '{nome}' ({quantidade_total} unidades)")
            
            resultado = {
                "success": True,
                "registros_lidos": total_records,
                "itens_unicos": len(items_agrupados),
                "items_novos": items_novos,
                "items_atualizados": items_atualizados
            }
            
            print(f"Sincronizacao concluida:")
            print(f"   - {total_records} registros lidos")
            print(f"   - {len(items_agrupados)} itens unicos")
            print(f"   - {items_novos} novos | {items_atualizados} atualizados")
            
            return resultado
            
        except Exception as e:
            print(f"Erro ao sincronizar com Google Sheets: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def update_item_quantity(self, item_name: str, new_quantity: int):
        """Update item quantity in Google Sheets (DISABLED - local DB only)"""
        # Não atualizamos o Google Sheets, apenas lemos dele
        # O controle de quantidade fica no banco local
        pass
    
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
                # Silenciosamente retorna vazio se não encontrar
                # (não é crítico para o funcionamento)
                return {}
                
        except Exception as e:
            # Silenciosamente retorna vazio em caso de erro
            return {}

