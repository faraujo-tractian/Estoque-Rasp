"""
Database Service
SQLite database operations
"""

import sqlite3
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.config import settings
from app.models.item import Item, Transaction


class Database:
    """Database handler for SQLite operations"""
    
    def __init__(self):
        self.db_path = settings.DATABASE_PATH
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Items table (versão agregada do 5S)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT,
                localizacao TEXT,
                quantidade_total INTEGER NOT NULL DEFAULT 0,
                quantidade_disponivel INTEGER NOT NULL DEFAULT 0,
                quantidade_em_uso INTEGER NOT NULL DEFAULT 0,
                estoque_minimo INTEGER NOT NULL DEFAULT 2,
                codigos_originais TEXT,
                aba_origem TEXT,
                ultima_sincronizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                item_id INTEGER NOT NULL,
                item_nome TEXT,
                quantidade INTEGER NOT NULL,
                nome_pessoa TEXT NOT NULL,
                saldo_apos INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items (id)
            )
        """)
        
        # Items em uso (rastreamento de unidades específicas)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items_em_uso (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                codigo_original TEXT,
                nome_pessoa TEXT NOT NULL,
                data_retirada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                previsao_devolucao TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items (id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_nome ON items(nome)")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_items_nome_aba ON items(nome, aba_origem)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_item ON transactions(item_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_em_uso_item ON items_em_uso(item_id)")
        
        conn.commit()
        conn.close()
    
    # ITEMS OPERATIONS
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all items"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items ORDER BY nome")
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    def get_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Get item by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_item_by_name(self, nome: str) -> Optional[Dict[str, Any]]:
        """Get item by name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE nome = ?", (nome,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def get_item_by_name_and_aba(self, nome: str, aba_origem: str) -> Optional[Dict[str, Any]]:
        """Get item by name and aba_origem"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE nome = ? AND aba_origem = ?", (nome, aba_origem))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
    
    def search_items(self, query: str) -> List[Dict[str, Any]]:
        """Search items by name"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM items WHERE nome LIKE ? ORDER BY nome LIMIT 20",
            (f"%{query}%",)
        )
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    def upsert_item(self, item_data: dict) -> int:
        """Insert or update item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Buscar por nome E aba_origem (índice único)
        cursor.execute(
            "SELECT id FROM items WHERE nome = ? AND aba_origem = ?", 
            (item_data['nome'], item_data.get('aba_origem'))
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            item_id = existing['id']
            cursor.execute("""
                UPDATE items 
                SET categoria = ?, localizacao = ?, quantidade_total = ?,
                    quantidade_disponivel = ?, quantidade_em_uso = ?,
                    estoque_minimo = ?, codigos_originais = ?, aba_origem = ?,
                    ultima_sincronizacao = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                item_data.get('categoria'),
                item_data.get('localizacao'),
                item_data.get('quantidade_total', 0),
                item_data.get('quantidade_disponivel', 0),
                item_data.get('quantidade_em_uso', 0),
                item_data.get('estoque_minimo', 2),
                item_data.get('codigos_originais'),
                item_data.get('aba_origem'),
                item_id
            ))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO items (
                    nome, categoria, localizacao, quantidade_total,
                    quantidade_disponivel, quantidade_em_uso, estoque_minimo,
                    codigos_originais, aba_origem, ultima_sincronizacao
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                item_data['nome'],
                item_data.get('categoria'),
                item_data.get('localizacao'),
                item_data.get('quantidade_total', 0),
                item_data.get('quantidade_disponivel', 0),
                item_data.get('quantidade_em_uso', 0),
                item_data.get('estoque_minimo', 2),
                item_data.get('codigos_originais'),
                item_data.get('aba_origem')
            ))
            item_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return item_id
    
    def update_item_quantity(self, item_id: int, new_quantity: int) -> bool:
        """Update item quantity"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE items SET quantidade_disponivel = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_quantity, item_id)
        )
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
    
    # TRANSACTIONS OPERATIONS
    
    def create_transaction(self, transaction: Transaction) -> int:
        """Create a new transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO transactions (tipo, item_id, item_nome, quantidade, nome_pessoa, saldo_apos, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (transaction.tipo, transaction.item_id, transaction.item_nome, 
              transaction.quantidade, transaction.nome_pessoa, transaction.saldo_apos,
              transaction.timestamp))
        
        transaction_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return transaction_id
    
    def get_transactions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent transactions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transactions
    
    def get_transactions_by_item(self, item_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get transactions for a specific item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM transactions WHERE item_id = ? ORDER BY timestamp DESC LIMIT ?",
            (item_id, limit)
        )
        transactions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return transactions
    
    # ITEMS EM USO OPERATIONS
    
    def add_item_em_uso(self, item_id: int, codigo: str, nome_pessoa: str) -> int:
        """Registra item em uso"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO items_em_uso (item_id, codigo_original, nome_pessoa)
            VALUES (?, ?, ?)
        """, (item_id, codigo, nome_pessoa))
        uso_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return uso_id
    
    def remove_item_em_uso(self, item_id: int, nome_pessoa: str, quantidade: int = 1):
        """Remove item de em uso"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM items_em_uso 
            WHERE item_id = ? AND nome_pessoa = ?
            LIMIT ?
        """, (item_id, nome_pessoa, quantidade))
        conn.commit()
        conn.close()
    
    def get_items_em_uso(self) -> List[Dict[str, Any]]:
        """Lista todos os itens em uso"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ieu.*, i.nome as item_nome, i.categoria
            FROM items_em_uso ieu
            JOIN items i ON ieu.item_id = i.id
            ORDER BY ieu.data_retirada DESC
        """)
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    def get_items_em_uso_by_item(self, item_id: int) -> List[Dict[str, Any]]:
        """Lista itens em uso de um item específico"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM items_em_uso 
            WHERE item_id = ?
            ORDER BY data_retirada DESC
        """, (item_id,))
        items = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return items
    
    def clear_all_data(self):
        """Clear all data (for sync purposes)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items")
        conn.commit()
        conn.close()

