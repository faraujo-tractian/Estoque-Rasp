# 📁 Estrutura do Projeto

```
Estoque-Rasp/
│
├── 📄 README.md                    # Documentação principal
├── 📄 SETUP.md                     # Guia completo de configuração
├── 📄 QUICKSTART.md                # Início rápido
├── 📄 PROJECT_STRUCTURE.md         # Este arquivo
├── 📄 .gitignore                   # Arquivos ignorados pelo Git
├── 🔧 setup.sh                     # Script de instalação (Linux/Mac)
│
├── 🎨 frontend/                    # INTERFACE WEB
│   ├── index.html                  # Página principal
│   ├── css/
│   │   ├── reset.css              # CSS Reset
│   │   ├── variables.css          # Variáveis CSS (cores, tamanhos)
│   │   └── main.css               # Estilos principais
│   └── js/
│       ├── config.js              # Configurações do frontend
│       ├── api.js                 # Comunicação com backend
│       ├── app.js                 # App principal
│       └── components/
│           ├── searchBar.js       # Componente de busca
│           ├── itemCard.js        # Componente de item selecionado
│           └── modal.js           # Modal de histórico
│
├── ⚙️  backend/                    # API BACKEND
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                # 🚀 Aplicação FastAPI principal
│   │   ├── config.py              # Configurações e variáveis de ambiente
│   │   │
│   │   ├── models/                # MODELOS DE DADOS
│   │   │   ├── __init__.py
│   │   │   └── item.py            # Models: Item, Transaction
│   │   │
│   │   ├── routes/                # ENDPOINTS DA API
│   │   │   ├── __init__.py
│   │   │   ├── items.py           # Rotas de itens
│   │   │   └── transactions.py    # Rotas de transações
│   │   │
│   │   ├── services/              # LÓGICA DE NEGÓCIO
│   │   │   ├── __init__.py
│   │   │   ├── database.py        # Operações SQLite
│   │   │   ├── google_sheets.py   # Integração Google Sheets
│   │   │   └── slack_service.py   # Integração Slack
│   │   │
│   │   └── utils/                 # UTILITÁRIOS
│   │       ├── __init__.py
│   │       └── validators.py      # Validações
│   │
│   ├── requirements.txt            # Dependências Python
│   ├── .env                        # ⚠️  Variáveis de ambiente (configure!)
│   ├── .env.example                # Template do .env
│   └── test_setup.py               # Script de verificação
│
├── 📊 data/                        # BANCO DE DADOS
│   ├── .gitkeep
│   └── estoque.db                  # SQLite (criado automaticamente)
│
└── 🔐 credentials/                 # CREDENCIAIS
    ├── .gitkeep
    └── google_sheets_key.json      # ⚠️  Credenciais Google (adicione!)
```

---

## 🎯 Componentes Principais

### Frontend (Interface Web)

| Arquivo | Função |
|---------|--------|
| `index.html` | Estrutura HTML da aplicação |
| `css/variables.css` | Variáveis de design (cores, espaçamentos) |
| `css/main.css` | Estilos principais e responsividade |
| `js/app.js` | Inicialização e orquestração |
| `js/api.js` | Comunicação com backend via fetch |
| `js/components/searchBar.js` | Busca de itens com debounce |
| `js/components/itemCard.js` | Exibição e ações do item selecionado |
| `js/components/modal.js` | Modal de histórico de movimentações |

### Backend (API)

| Arquivo | Função |
|---------|--------|
| `app/main.py` | FastAPI app, rotas principais, startup/shutdown |
| `app/config.py` | Carregamento de variáveis de ambiente |
| `app/models/item.py` | Modelos Pydantic (Item, Transaction) |
| `app/routes/items.py` | Endpoints de itens (/items, /search) |
| `app/routes/transactions.py` | Endpoints de transações (/transactions, /history) |
| `app/services/database.py` | CRUD operations no SQLite |
| `app/services/google_sheets.py` | Sincronização bidirecional com Google Sheets |
| `app/services/slack_service.py` | Envio de notificações ao Slack |

---

## 🔄 Fluxo de Dados

```
┌─────────────┐
│   Browser   │ ← Interface Touch-Friendly
└──────┬──────┘
       │ HTTP/JSON
       ▼
┌─────────────┐
│  FastAPI    │ ← Backend Python
│  (Port 8000)│
└──────┬──────┘
       │
   ┌───┴────┬────────┬─────────┐
   ▼        ▼        ▼         ▼
┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐
│SQLite│ │Sheets│ │Slack │ │Cache │
└──────┘ └──────┘ └──────┘ └──────┘
  Local   Cloud   Notif.  Offline
```

---

## 📦 Tecnologias Utilizadas

### Frontend
- HTML5
- CSS3 (Custom Properties)
- Vanilla JavaScript (ES6+)
- Fetch API

### Backend
- Python 3.8+
- FastAPI (Web Framework)
- Uvicorn (ASGI Server)
- SQLite3 (Database)
- Pydantic (Validation)

### Integrações
- gspread (Google Sheets API)
- slack-sdk (Slack API)
- APScheduler (Task Scheduling)

---

## 🎨 Design System

O frontend utiliza um design system baseado em variáveis CSS:

- **Cores:** Primary, Success, Danger, Warning
- **Espaçamentos:** xs, sm, md, lg, xl
- **Tipografia:** sm, base, lg, xl, 2xl, 3xl
- **Touch Targets:** Mínimo 44x44px (otimizado para touch)

---

## 🔒 Segurança

⚠️ **Arquivos sensíveis (NÃO commitar):**
- `backend/.env`
- `credentials/google_sheets_key.json`
- `data/estoque.db`

✅ **Incluídos no .gitignore**

---

## 📚 Documentação

| Arquivo | Conteúdo |
|---------|----------|
| `README.md` | Visão geral, features, instalação básica |
| `SETUP.md` | Guia passo a passo completo |
| `QUICKSTART.md` | Início rápido em 5 minutos |
| `PROJECT_STRUCTURE.md` | Este arquivo - estrutura do projeto |

---

## 🚀 Como Começar

1. **Configuração:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Credenciais:**
   - Adicionar `google_sheets_key.json` em `credentials/`
   - Editar `backend/.env` com suas configurações

3. **Executar:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

4. **Acessar:**
   - Local: http://localhost:8000
   - Rede: http://[IP_DO_SERVIDOR]:8000

---

**Desenvolvido para controle de estoque com metodologia 5S**

