"""
Data Models for Items and Transactions
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Item(BaseModel):
    """Item Model"""
    id: Optional[int] = None
    nome: str
    categoria: Optional[str] = None
    quantidade_disponivel: int
    estoque_minimo: int = 0
    localizacao: Optional[str] = None
    
    class Config:
        from_attributes = True


class Transaction(BaseModel):
    """Transaction Model"""
    id: Optional[int] = None
    tipo: str  # 'retirada' or 'devolucao'
    item_id: int
    item_nome: Optional[str] = None
    quantidade: int
    nome_pessoa: str
    saldo_apos: int
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    """Transaction Creation Request"""
    tipo: str = Field(..., pattern="^(retirada|devolucao)$")
    item_id: int
    quantidade: int = Field(..., gt=0)
    nome_pessoa: str = Field(..., min_length=1)


class TransactionResponse(BaseModel):
    """Transaction Response"""
    success: bool
    message: str
    transaction_id: int
    novo_saldo: int
    slack_notified: bool = False

