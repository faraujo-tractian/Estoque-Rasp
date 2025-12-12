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
        
        # Items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                categoria TEXT,
                quantidade_disponivel INTEGER NOT NULL DEFAULT 0,
                estoque_minimo INTEGER NOT NULL DEFAULT 0,
                localizacao TEXT,
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
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_nome ON items(nome)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp DESC)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_item ON transactions(item_id)")
        
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
    
    def upsert_item(self, item: Item) -> int:
        """Insert or update item"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if item.id:
            # Update existing
            cursor.execute("""
                UPDATE items 
                SET nome = ?, categoria = ?, quantidade_disponivel = ?, 
                    estoque_minimo = ?, localizacao = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (item.nome, item.categoria, item.quantidade_disponivel, 
                  item.estoque_minimo, item.localizacao, item.id))
            item_id = item.id
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO items (nome, categoria, quantidade_disponivel, estoque_minimo, localizacao)
                VALUES (?, ?, ?, ?, ?)
            """, (item.nome, item.categoria, item.quantidade_disponivel, 
                  item.estoque_minimo, item.localizacao))
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
    
    def clear_all_data(self):
        """Clear all data (for sync purposes)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items")
        conn.commit()
        conn.close()

