# 🛠️ Guia de Configuração Completo

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Configurar Google Sheets](#configurar-google-sheets)
3. [Configurar Slack Bot](#configurar-slack-bot)
4. [Instalar na Raspberry Pi](#instalar-na-raspberry-pi)
5. [Configurar Inicialização Automática](#configurar-inicialização-automática)
6. [Testar o Sistema](#testar-o-sistema)

---

## 🎯 Pré-requisitos

- Raspberry Pi 3 ou superior (ou qualquer Linux)
- Sistema operacional: Raspberry Pi OS (Buster ou mais recente)
- Acesso à internet
- Conta Google
- Workspace Slack

---

## 📊 Configurar Google Sheets

### 1. Criar a Planilha

Crie uma nova planilha no Google Sheets com 3 abas:

#### **Aba 1: ITENS**

| ID | Item | Categoria | Qtd_Disponível | Estoque_Mínimo | Localização |
|----|------|-----------|----------------|----------------|-------------|
| 1 | Parafuso M8 | Fixação | 200 | 50 | Prateleira A1 |
| 2 | Chave Phillips | Ferramentas | 15 | 5 | Caixa 3 |

#### **Aba 2: HISTÓRICO**

| Data/Hora | Tipo | Item | Quantidade | Usuário | Saldo Após | Observações |
|-----------|------|------|------------|---------|------------|-------------|

*(Será preenchida automaticamente)*

#### **Aba 3: PESSOAS** *(Opcional)*

| Nome | Slack_Username | Slack_User_ID |
|------|----------------|---------------|
| Felipe Araújo | @felipe | U12345ABC |
| Maria Silva | @maria | U67890DEF |

### 2. Criar Service Account

1. Acesse: https://console.cloud.google.com/
2. Crie um novo projeto: "Sistema Estoque"
3. Ative a **Google Sheets API**:
   - Menu → APIs & Services → Library
   - Busque "Google Sheets API" → Enable

4. Criar credenciais:
   - APIs & Services → Credentials
   - Create Credentials → Service Account
   - Nome: "estoque-bot"
   - Clique em Create
   - Pule as permissões opcionais
   - Done

5. Criar chave:
   - Clique no service account criado
   - Keys → Add Key → Create New Key
   - JSON → Create
   - **Salve o arquivo baixado**

6. Compartilhar planilha:
   - Abra o arquivo JSON baixado
   - Copie o email `client_email` (algo como: `estoque-bot@projeto.iam.gserviceaccount.com`)
   - Na sua planilha, clique em "Compartilhar"
   - Cole o email e dê permissão de **Editor**

7. Copiar ID da planilha:
   - Na URL da planilha: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
   - Copie o `SPREADSHEET_ID`

---

## 💬 Configurar Slack Bot

### 1. Criar o App

1. Acesse: https://api.slack.com/apps
2. Clique em **Create New App**
3. Escolha **From scratch**
4. Nome: "Estoque Bot"
5. Selecione seu workspace

### 2. Configurar Permissões

1. No menu lateral: **OAuth & Permissions**
2. Em **Scopes** → **Bot Token Scopes**, adicione:
   - `chat:write` - Enviar mensagens
   - `users:read` - Ler informações de usuários
   - `channels:read` - Acessar canais

### 3. Instalar no Workspace

1. No topo da página: **Install to Workspace**
2. Autorize
3. **Copie o Bot User OAuth Token** (começa com `xoxb-`)

### 4. Adicionar ao Canal

1. No Slack, vá ao canal desejado (ex: `#estoque`)
2. Digite: `/invite @Estoque Bot`
3. Ou clique em "Adicionar pessoas ao canal" e procure o bot

### 5. Obter User ID do Supervisor *(Opcional)*

Para mencionar o supervisor quando estoque está baixo:

1. No Slack, clique no perfil do supervisor
2. Menu → Copiar ID do membro
3. Será algo como: `U12345ABCD`

---

## 🍓 Instalar na Raspberry Pi

### 1. Conectar na Raspberry Pi

```bash
ssh pi@raspberrypi.local
# Senha padrão: raspberry
```

### 2. Atualizar Sistema

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 3. Instalar Dependências

```bash
sudo apt-get install -y python3 python3-pip python3-venv git
```

### 4. Clonar/Copiar Projeto

**Opção A: Se tiver Git**
```bash
cd ~
git clone [URL_DO_SEU_REPOSITORIO] Estoque-Rasp
cd Estoque-Rasp
```

**Opção B: Copiar via SCP**
```bash
# No seu computador:
scp -r Estoque-Rasp pi@raspberrypi.local:~/
```

### 5. Executar Setup

```bash
cd ~/Estoque-Rasp
chmod +x setup.sh
./setup.sh
```

### 6. Adicionar Credenciais

**Google Sheets:**
```bash
# Copie o arquivo JSON baixado para a Raspberry Pi
scp google_sheets_key.json pi@raspberrypi.local:~/Estoque-Rasp/credentials/
```

**Configurar .env:**
```bash
nano backend/.env
```

Preencha:
```env
GOOGLE_SHEETS_SPREADSHEET_ID=cole_o_id_aqui
SLACK_BOT_TOKEN=xoxb-cole-o-token-aqui
SLACK_CHANNEL=#estoque
SLACK_SUPERVISOR_ID=U12345ABCD
```

Salve: `Ctrl+O` → Enter → `Ctrl+X`

### 7. Testar Manualmente

```bash
cd ~/Estoque-Rasp/backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Acesse no navegador: `http://raspberrypi.local:8000`

---

## 🚀 Configurar Inicialização Automática

### 1. Criar Serviço Systemd

```bash
sudo nano /etc/systemd/system/estoque.service
```

Cole o seguinte:

```ini
[Unit]
Description=Sistema de Controle de Estoque 5S
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Estoque-Rasp/backend
Environment="PATH=/home/pi/Estoque-Rasp/backend/venv/bin"
ExecStart=/home/pi/Estoque-Rasp/backend/venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Salve: `Ctrl+O` → Enter → `Ctrl+X`

### 2. Ativar Serviço

```bash
sudo systemctl daemon-reload
sudo systemctl enable estoque.service
sudo systemctl start estoque.service
```

### 3. Verificar Status

```bash
sudo systemctl status estoque.service
```

Deve mostrar: `Active: active (running)`

### 4. Ver Logs

```bash
# Logs em tempo real
sudo journalctl -u estoque.service -f

# Últimas 100 linhas
sudo journalctl -u estoque.service -n 100
```

---

## 🖥️ Configurar Modo Kiosk (Tela Touch)

### 1. Instalar Chromium

```bash
sudo apt-get install -y chromium-browser unclutter
```

### 2. Configurar Autostart

```bash
mkdir -p ~/.config/lxsession/LXDE-pi
nano ~/.config/lxsession/LXDE-pi/autostart
```

Adicione:

```
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi
@xscreensaver -no-splash

# Esconder cursor após 0.1s de inatividade
@unclutter -idle 0.1 -root

# Desabilitar screensaver
@xset s off
@xset -dpms
@xset s noblank

# Abrir navegador em modo kiosk
@chromium-browser --kiosk --app=http://localhost:8000 --incognito --disable-pinch --overscroll-history-navigation=0
```

Salve e reinicie:

```bash
sudo reboot
```

---

## ✅ Testar o Sistema

### 1. Teste Básico

1. Abra o navegador: `http://raspberrypi.local:8000` (ou IP da Rasp)
2. Digite seu nome
3. Busque um item
4. Tente fazer uma retirada

### 2. Verificar Slack

- Uma mensagem deve aparecer no canal configurado
- Se você configurou PESSOAS no Sheets, deve mencionar seu @

### 3. Verificar Google Sheets

- O histórico deve ser atualizado
- A quantidade do item deve diminuir

### 4. Teste de Estoque Baixo

- Retire itens até ficar abaixo do estoque mínimo
- O supervisor deve ser mencionado no Slack

---

## 🔧 Comandos Úteis

```bash
# Reiniciar serviço
sudo systemctl restart estoque.service

# Parar serviço
sudo systemctl stop estoque.service

# Ver logs
sudo journalctl -u estoque.service -f

# Ver IP da Raspberry Pi
hostname -I

# Testar conexão com backend
curl http://localhost:8000/api/health
```

---

## 🆘 Troubleshooting

### Problema: Google Sheets não sincroniza

**Solução:**
```bash
# Ver logs
sudo journalctl -u estoque.service -n 100

# Verificar se o arquivo existe
ls -la ~/Estoque-Rasp/credentials/google_sheets_key.json

# Testar manualmente
cd ~/Estoque-Rasp/backend
source venv/bin/activate
python -c "from app.services.google_sheets import GoogleSheetsService; import asyncio; asyncio.run(GoogleSheetsService().sync_from_sheets())"
```

### Problema: Slack não envia mensagens

**Solução:**
```bash
# Verificar token no .env
cat ~/Estoque-Rasp/backend/.env | grep SLACK

# Testar token
curl -H "Authorization: Bearer xoxb-SEU-TOKEN" https://api.slack.com/api/auth.test
```

### Problema: Porta 8000 em uso

**Solução:**
```bash
# Ver processo usando a porta
sudo lsof -i :8000

# Matar processo
sudo kill -9 [PID]

# Ou reiniciar serviço
sudo systemctl restart estoque.service
```

---

## 🎉 Pronto!

Seu sistema está configurado e funcionando!

**Próximos passos:**
- Compartilhe o IP da Raspberry Pi com a equipe
- Todos podem acessar pelo celular/PC: `http://IP_DA_RASP:8000`
- Configure WiFi na Rasp para acesso remoto
- Considere usar um domínio local (ex: `estoque.local`)

---

**💡 Dica Final:** Faça backup regular da planilha do Google Sheets!

