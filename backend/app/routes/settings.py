"""Settings routes - configuration endpoints"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import settings
import os
from pathlib import Path

router = APIRouter()


class SlackSettings(BaseModel):
    """Slack settings model"""
    enabled: bool


class SlackSettingsResponse(BaseModel):
    """Slack settings response"""
    channel: str
    enabled: bool
    configured: bool


@router.get("/settings/slack", response_model=SlackSettingsResponse)
async def get_slack_settings():
    """Get current Slack settings"""
    return SlackSettingsResponse(
        channel=settings.SLACK_CHANNEL,
        enabled=settings.SLACK_ENABLED,
        configured=bool(settings.SLACK_BOT_TOKEN and settings.SLACK_CHANNEL)
    )


@router.post("/settings/slack")
async def save_slack_settings(slack_settings: SlackSettings):
    """Save Slack settings to .env file"""
    try:
        env_path = Path(__file__).parent.parent.parent / ".env"
        
        # Read current .env content
        if env_path.exists():
            with open(env_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Update SLACK_ENABLED value
        found = False
        for i, line in enumerate(lines):
            if line.strip().startswith('SLACK_ENABLED='):
                lines[i] = f'SLACK_ENABLED={slack_settings.enabled}\n'
                found = True
                break
        
        # Add if not found
        if not found:
            lines.append(f'\nSLACK_ENABLED={slack_settings.enabled}\n')
        
        # Write back to .env
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        # Update runtime settings
        settings.SLACK_ENABLED = slack_settings.enabled
        
        return {
            "success": True,
            "message": "Configuracoes do Slack atualizadas com sucesso"
        }
        
    except Exception as e:
        print(f"Erro ao salvar configuracoes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar configuracoes: {str(e)}"
        )

