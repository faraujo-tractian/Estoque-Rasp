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
        
        # Calculate new quantities
        if transaction_data.tipo == "retirada":
            # Check if there's enough stock
            if item['quantidade_disponivel'] < transaction_data.quantidade:
                raise HTTPException(
                    status_code=400,
                    detail=f"Estoque insuficiente! Disponível: {item['quantidade_disponivel']} unidades"
                )
            new_disponivel = item['quantidade_disponivel'] - transaction_data.quantidade
            new_em_uso = item['quantidade_em_uso'] + transaction_data.quantidade
        else:  # devolucao
            # Check if there are items in use to return
            if item['quantidade_em_uso'] < transaction_data.quantidade:
                raise HTTPException(
                    status_code=400,
                    detail=f"Quantidade inválida! Apenas {item['quantidade_em_uso']} unidades em uso"
                )
            new_disponivel = item['quantidade_disponivel'] + transaction_data.quantidade
            new_em_uso = item['quantidade_em_uso'] - transaction_data.quantidade
        
        new_quantity = new_disponivel  # Para compatibilidade com código existente
        
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
        
        # Update item quantities in database
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE items 
            SET quantidade_disponivel = ?,
                quantidade_em_uso = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (new_disponivel, new_em_uso, transaction_data.item_id))
        conn.commit()
        conn.close()
        
        # Registrar em items_em_uso (opcional - apenas track de códigos)
        if transaction_data.tipo == "retirada":
            # Pegar códigos disponíveis
            codigos = item.get('codigos_originais', '').split(',')
            for i in range(transaction_data.quantidade):
                if i < len(codigos):
                    db.add_item_em_uso(transaction_data.item_id, codigos[i], transaction_data.nome_pessoa)
        else:
            # Remover de items_em_uso
            db.remove_item_em_uso(transaction_data.item_id, transaction_data.nome_pessoa, transaction_data.quantidade)
        
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
        print(f"Erro ao processar transacao: {e}")
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


@router.get("/items-em-uso")
async def get_items_em_uso():
    """Get all items currently in use"""
    try:
        items = db.get_items_em_uso()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/items-em-uso/item/{item_id}")
async def get_item_em_uso(item_id: int):
    """Get items in use for a specific item"""
    try:
        items = db.get_items_em_uso_by_item(item_id)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

