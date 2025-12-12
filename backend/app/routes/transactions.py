"""
Transactions Routes
Endpoints for item transactions (retirada/devolucao)
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
from datetime import datetime
from app.services.database import Database
from app.services.slack_service import SlackService
from app.services.google_sheets import GoogleSheetsService
from app.models.item import Transaction, TransactionCreate, TransactionResponse

router = APIRouter()
db = Database()
slack_service = SlackService()


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(transaction_data: TransactionCreate):
    """
    Create a new transaction (retirada or devolucao)
    """
    try:
        # Get item
        item = db.get_item_by_id(transaction_data.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        
        # Calculate new quantity
        if transaction_data.tipo == "retirada":
            # Check if there's enough stock
            if item['quantidade_disponivel'] < transaction_data.quantidade:
                raise HTTPException(
                    status_code=400,
                    detail=f"Estoque insuficiente! Disponível: {item['quantidade_disponivel']} unidades"
                )
            new_quantity = item['quantidade_disponivel'] - transaction_data.quantidade
        else:  # devolucao
            new_quantity = item['quantidade_disponivel'] + transaction_data.quantidade
        
        # Create transaction record
        transaction = Transaction(
            tipo=transaction_data.tipo,
            item_id=transaction_data.item_id,
            item_nome=item['nome'],
            quantidade=transaction_data.quantidade,
            nome_pessoa=transaction_data.nome_pessoa,
            saldo_apos=new_quantity,
            timestamp=datetime.now()
        )
        
        transaction_id = db.create_transaction(transaction)
        
        # Update item quantity in database
        db.update_item_quantity(transaction_data.item_id, new_quantity)
        
        # Try to get Slack user ID from Google Sheets mapping
        user_slack_id = None
        try:
            sheets_service = GoogleSheetsService()
            user_mapping = sheets_service.get_slack_user_mapping()
            user_slack_id = user_mapping.get(transaction_data.nome_pessoa.lower())
            
            # If not found in mapping, try to search Slack directly
            if not user_slack_id:
                user_slack_id = slack_service.find_user_by_name(transaction_data.nome_pessoa)
        except Exception as e:
            print(f"⚠️  Erro ao buscar usuário no Slack: {e}")
        
        # Send Slack notification
        slack_notified = False
        try:
            slack_notified = await slack_service.send_transaction_notification(
                tipo=transaction_data.tipo,
                item_nome=item['nome'],
                quantidade=transaction_data.quantidade,
                nome_pessoa=transaction_data.nome_pessoa,
                user_id=user_slack_id,
                saldo_atual=new_quantity,
                estoque_minimo=item['estoque_minimo']
            )
        except Exception as e:
            print(f"⚠️  Erro ao enviar notificação ao Slack: {e}")
        
        # Update Google Sheets
        try:
            sheets_service = GoogleSheetsService()
            await sheets_service.update_item_quantity(item['nome'], new_quantity)
            await sheets_service.append_to_history({
                'timestamp': transaction.timestamp.isoformat(),
                'tipo': transaction_data.tipo,
                'item_nome': item['nome'],
                'quantidade': transaction_data.quantidade,
                'nome_pessoa': transaction_data.nome_pessoa,
                'saldo_apos': new_quantity
            })
        except Exception as e:
            print(f"⚠️  Erro ao atualizar Google Sheets: {e}")
        
        return TransactionResponse(
            success=True,
            message=f"{'Retirada' if transaction_data.tipo == 'retirada' else 'Devolução'} realizada com sucesso!",
            transaction_id=transaction_id,
            novo_saldo=new_quantity,
            slack_notified=slack_notified
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao processar transação: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history(limit: int = Query(50, ge=1, le=200)):
    """Get transaction history"""
    try:
        transactions = db.get_transactions(limit)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/item/{item_id}")
async def get_item_history(item_id: int, limit: int = Query(20, ge=1, le=100)):
    """Get transaction history for a specific item"""
    try:
        transactions = db.get_transactions_by_item(item_id, limit)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

