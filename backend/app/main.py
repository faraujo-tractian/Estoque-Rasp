"""
Main FastAPI Application
Sistema de Controle de Estoque 5S
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.routes import items, transactions, settings as settings_routes
from app.services.database import Database
from app.services.google_sheets import GoogleSheetsService
from app.config import settings


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Iniciando aplicacao...")
    
    # Initialize database
    db = Database()
    db.init_db()
    print("Banco de dados inicializado")
    
    # Initial sync with Google Sheets
    try:
        print("Iniciando sincronizacao com Google Sheets...")
        sheets_service = GoogleSheetsService()
        result = await sheets_service.sync_from_sheets()
        print(f"Sincronizacao inicial concluida: {result}")
    except Exception as e:
        print(f"Erro na sincronizacao inicial: {e}")
        print("   Sistema continuara funcionando com dados locais")
        import traceback
        traceback.print_exc()
    
    yield
    
    # Shutdown
    print("Encerrando aplicacao...")


# Create FastAPI app
app = FastAPI(
    title="Sistema de Controle de Estoque 5S",
    description="API para gerenciamento de estoque com integração Google Sheets e Slack",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(items.router, prefix="/api", tags=["Items"])
app.include_router(transactions.router, prefix="/api", tags=["Transactions"])
app.include_router(settings_routes.router, prefix="/api", tags=["Settings"])

# Mount static files (frontend)
frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend HTML"""
        return FileResponse(os.path.join(frontend_path, "index.html"))


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

