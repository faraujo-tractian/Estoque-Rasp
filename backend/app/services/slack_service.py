"""
Slack Service
Handles Slack notifications
"""

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from typing import Optional, Dict
from app.config import settings


class SlackService:
    """Slack integration service"""
    
    def __init__(self):
        self.token = settings.SLACK_BOT_TOKEN
        self.channel = settings.SLACK_CHANNEL
        self.enabled = settings.SLACK_ENABLED
        self.client = None
        
        if self.token:
            self.client = WebClient(token=self.token)
    
    def is_configured(self) -> bool:
        """Check if Slack is properly configured AND enabled"""
        return bool(self.enabled and self.token and self.client)
    
    def find_user_by_name(self, name: str) -> Optional[str]:
        """Find Slack user ID by name"""
        if not self.is_configured():
            return None
        
        try:
            # Search users
            response = self.client.users_list()
            users = response['members']
            
            name_lower = name.lower()
            
            for user in users:
                # Check real name or display name
                real_name = user.get('real_name', '').lower()
                display_name = user.get('profile', {}).get('display_name', '').lower()
                
                if name_lower in real_name or name_lower in display_name:
                    return user['id']
            
            return None
            
        except SlackApiError as e:
            print(f"⚠️  Erro ao buscar usuário no Slack: {e}")
            return None
    
    def get_user_mention(self, user_id: Optional[str], fallback_name: str) -> str:
        """Get user mention string or fallback to name"""
        if user_id:
            return f"<@{user_id}>"
        return fallback_name
    
    async def send_transaction_notification(
        self,
        tipo: str,
        item_nome: str,
        quantidade: int,
        nome_pessoa: str,
        user_id: Optional[str],
        saldo_atual: int,
        estoque_minimo: int = 0
    ) -> bool:
        """Send transaction notification to Slack"""
        
        if not self.is_configured():
            print("Slack nao configurado ou desabilitado")
            return False
        
        try:
            # Determine emoji and action text
            emoji = "📤" if tipo == "retirada" else "📥"
            action = "RETIRADA" if tipo == "retirada" else "DEVOLUÇÃO"
            
            # Get user mention
            user_mention = self.get_user_mention(user_id, nome_pessoa)
            
            # Build message (sem alerta de estoque baixo)
            message = (
                f"{emoji} *{action}*\n"
                f"*Item:* {item_nome}\n"
                f"*Quantidade:* {quantidade} unidade(s)\n"
                f"*Responsável:* {user_mention}\n"
                f"*Saldo atual:* {saldo_atual} unidade(s)"
            )
            
            # Send message
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=message,
                mrkdwn=True
            )
            
            return response['ok']
            
        except SlackApiError as e:
            print(f"Erro ao enviar mensagem ao Slack: {e}")
            return False
    
    async def send_custom_message(self, message: str) -> bool:
        """Send custom message to Slack channel"""
        
        if not self.is_configured():
            return False
        
        try:
            response = self.client.chat_postMessage(
                channel=self.channel,
                text=message,
                mrkdwn=True
            )
            return response['ok']
        except SlackApiError as e:
            print(f"❌ Erro ao enviar mensagem ao Slack: {e}")
            return False

