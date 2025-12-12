"""
Validation Utilities
"""

from typing import Optional


def validate_transaction_type(tipo: str) -> bool:
    """Validate transaction type"""
    return tipo in ['retirada', 'devolucao']


def validate_quantity(quantidade: int) -> bool:
    """Validate quantity is positive"""
    return quantidade > 0


def validate_stock_availability(available: int, requested: int) -> bool:
    """Validate if requested quantity is available"""
    return available >= requested


def normalize_name(name: str) -> str:
    """Normalize name for comparison"""
    return name.strip().lower()

