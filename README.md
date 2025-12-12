# 📦 Sistema de Controle de Estoque 5S

Sistema completo para gerenciamento de estoque com interface touch-friendly, integração com Google Sheets e notificações no Slack.

## 🎯 Funcionalidades

- ✅ Interface web responsiva e touch-friendly
- ✅ Retirada e devolução de itens
- ✅ Sincronização automática com Google Sheets
- ✅ Notificações no Slack com menção de usuários
- ✅ Alertas quando estoque está baixo
- ✅ Histórico completo de movimentações
- ✅ Funciona offline com cache local (SQLite)
- ✅ Busca rápida de itens

## 🏗️ Arquitetura

```
Estoque-Rasp/
├── frontend/           # Interface Web (HTML/CSS/JS)
│   ├── css/           # Estilos
│   ├── js/            # JavaScript modular
│   └── index.html     # Página principal
│
├── backend/           # API Backend (FastAPI + Python)
│   ├── app/
│   │   ├── models/    # Modelos de dados
│   │   ├── routes/    # Endpoints da API
│   │   ├── services/  # Lógica de negócio
│   │   └── utils/     # Utilitários
│   └── requirements.txt
│
├── data/              # Banco de dados SQLite
└── credentials/       # Credenciais Google Sheets
```

## 🚀 Configuração

### 1. Pré-requisitos

- Python 3.8+
- Conta Google (para Google Sheets)
- Workspace Slack com permissões para criar apps

### 2. Configurar Google Sheets

1. Crie uma planilha no Google Sheets com as seguintes abas:

**Aba: ITENS**
```
| ID | Item | Categoria | Qtd_Disponível | Estoque_Mínimo | Localização |
```

**Aba: HISTÓRICO**
```
| Data/Hora | Tipo | Item | Quantidade | Usuário | Saldo Após | Observações |
```

**Aba: PESSOAS** (opcional - para mapear nomes → Slack)
```
| Nome | Slack_Username | Slack_User_ID |
```

**Aba: CONFIGURAÇÕES** (opcional)
```
| Chave | Valor |
| supervisor_slack_id | U12345ABC |
| canal_notificacoes | #estoque |
```

2. Criar Service Account no Google Cloud:
   - Acesse https://console.cloud.google.com/
   - Crie um novo projeto
   - Ative a Google Sheets API
   - Crie uma Service Account
   - Baixe o arquivo JSON de credenciais
   - Coloque em `credentials/google_sheets_key.json`
   - Compartilhe sua planilha com o email da service account

### 3. Configurar Slack Bot

1. Acesse https://api.slack.com/apps
2. Crie um novo app
3. Adicione as seguintes permissões (OAuth Scopes):
   - `chat:write` - Enviar mensagens
   - `users:read` - Buscar usuários
   - `channels:read` - Acessar canais
4. Instale o app no seu workspace
5. Copie o **Bot User OAuth Token** (começa com `xoxb-`)
6. Adicione o bot ao canal desejado (ex: `#estoque`)

### 4. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 5. Configurar Variáveis de Ambiente

```bash
cp backend/.env.example backend/.env
```

Edite o arquivo `.env` com suas credenciais:

```env
GOOGLE_SHEETS_SPREADSHEET_ID=seu_id_da_planilha
SLACK_BOT_TOKEN=xoxb-seu-token-aqui
SLACK_CHANNEL=#estoque
SLACK_SUPERVISOR_ID=U12345ABCD
```

### 6. Executar o Sistema

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Acesse: http://localhost:8000

## 📱 Uso na Raspberry Pi

### Configurar para iniciar automaticamente:

1. Crie um serviço systemd:

```bash
sudo nano /etc/systemd/system/estoque.service
```

```ini
[Unit]
Description=Sistema de Estoque 5S
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Estoque-Rasp/backend
ExecStart=/usr/bin/python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

2. Ativar e iniciar o serviço:

```bash
sudo systemctl enable estoque.service
sudo systemctl start estoque.service
```

3. Configurar navegador para abrir automaticamente (kiosk mode):

```bash
# Instalar chromium
sudo apt-get install chromium-browser unclutter

# Editar autostart
nano ~/.config/lxsession/LXDE-pi/autostart
```

Adicione:

```
@chromium-browser --kiosk --app=http://localhost:8000
@unclutter -idle 0
```

## 🔧 Desenvolvimento

### Estrutura de API

**GET** `/api/items` - Listar todos os itens
**GET** `/api/items/{id}` - Obter item específico  
**GET** `/api/items/search?q=termo` - Buscar itens

**POST** `/api/transactions` - Criar transação (retirada/devolução)
**GET** `/api/history` - Obter histórico
**GET** `/api/history/item/{id}` - Histórico de um item

**POST** `/api/sync` - Sincronizar com Google Sheets manualmente
**GET** `/api/health` - Health check

### Exemplo de Requisição

```javascript
// Retirar item
fetch('/api/transactions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        tipo: 'retirada',
        item_id: 1,
        quantidade: 5,
        nome_pessoa: 'Felipe Araújo'
    })
});
```

## 📊 Fluxo de Funcionamento

1. **Usuário digita nome** e busca item
2. **Seleciona quantidade** e ação (retirar/devolver)
3. **Sistema valida** disponibilidade
4. **Atualiza banco local** (SQLite)
5. **Busca @ do usuário** no Google Sheets ou Slack
6. **Envia notificação** ao Slack com menção
7. **Verifica estoque mínimo** e alerta supervisor se necessário
8. **Atualiza Google Sheets** (quantidade + histórico)
9. **Sincronização periódica** a cada 5 minutos

## 🎨 Personalização

### Alterar cores (CSS):

Edite `frontend/css/variables.css`:

```css
:root {
    --color-primary: #2563eb;  /* Azul principal */
    --color-success: #10b981;  /* Verde */
    --color-danger: #ef4444;   /* Vermelho */
}
```

### Alterar intervalo de sincronização:

No arquivo `.env`:
```env
SYNC_INTERVAL_MINUTES=5
```

## 🐛 Troubleshooting

### Google Sheets não sincroniza

- Verifique se a service account tem acesso à planilha
- Confirme o SPREADSHEET_ID no `.env`
- Veja os logs: `sudo journalctl -u estoque.service -f`

### Slack não envia mensagens

- Verifique se o bot foi adicionado ao canal
- Confirme as permissões do bot
- Teste o token: https://api.slack.com/methods/auth.test/test

### Erro de porta em uso

```bash
# Matar processo na porta 8000
sudo lsof -t -i:8000 | xargs sudo kill -9
```

## 📝 Licença

MIT License

## 👤 Autor

Desenvolvido para controle de estoque com metodologia 5S

---

**💡 Dica:** Acesse pelo IP da Raspberry Pi em qualquer dispositivo na mesma rede!
Exemplo: `http://192.168.1.100:8000`

