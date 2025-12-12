# 🚀 Quick Start - Sistema de Estoque 5S

## ⚡ Início Rápido (5 minutos)

### 1️⃣ Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2️⃣ Configurar Credenciais

**Google Sheets:**
1. Coloque `google_sheets_key.json` na pasta `credentials/`
2. Edite `backend/.env` e adicione o `GOOGLE_SHEETS_SPREADSHEET_ID`

**Slack:**
1. Edite `backend/.env` e adicione o `SLACK_BOT_TOKEN`

### 3️⃣ Executar

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4️⃣ Acessar

Abra no navegador: **http://localhost:8000**

---

## 📋 Checklist de Configuração

- [ ] Python 3.8+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `credentials/google_sheets_key.json` adicionado
- [ ] Variáveis configuradas no `backend/.env`:
  - [ ] `GOOGLE_SHEETS_SPREADSHEET_ID`
  - [ ] `SLACK_BOT_TOKEN`
  - [ ] `SLACK_CHANNEL`
  - [ ] `SLACK_SUPERVISOR_ID` (opcional)
- [ ] Planilha Google Sheets criada com abas: ITENS, HISTÓRICO, PESSOAS
- [ ] Planilha compartilhada com service account
- [ ] Slack Bot adicionado ao canal

---

## 🧪 Testar Configuração

```bash
python test_setup.py
```

Este script verifica se tudo está configurado corretamente.

---

## 🎯 Estrutura da Planilha

### Aba: ITENS
```
ID | Item | Categoria | Qtd_Disponível | Estoque_Mínimo | Localização
1  | Exemplo | Categoria A | 100 | 20 | Prateleira 1
```

### Aba: HISTÓRICO
*(Será preenchida automaticamente pelo sistema)*

### Aba: PESSOAS *(Opcional)*
```
Nome | Slack_Username | Slack_User_ID
João Silva | @joao | U12345ABC
```

---

## 🔗 Endpoints da API

- `GET /api/items` - Listar itens
- `GET /api/items/search?q=termo` - Buscar itens
- `POST /api/transactions` - Criar transação
- `GET /api/history` - Ver histórico
- `POST /api/sync` - Sincronizar com Google Sheets
- `GET /api/health` - Health check

---

## 📱 Acessar de Outros Dispositivos

Descubra o IP do servidor:

```bash
# Linux/Mac
hostname -I

# Windows
ipconfig
```

Acesse de qualquer dispositivo na mesma rede:
```
http://IP_DO_SERVIDOR:8000
```

Exemplo: `http://192.168.1.100:8000`

---

## 🐛 Problemas Comuns

### Erro: "ModuleNotFoundError"
```bash
pip install -r backend/requirements.txt
```

### Erro: "Google Sheets não sincroniza"
- Verifique se o arquivo `google_sheets_key.json` está em `credentials/`
- Confirme que a planilha está compartilhada com o email do service account
- Verifique o `SPREADSHEET_ID` no `.env`

### Erro: "Slack não envia mensagens"
- Verifique o `SLACK_BOT_TOKEN` no `.env`
- Confirme que o bot foi adicionado ao canal
- Teste o token: `curl -H "Authorization: Bearer TOKEN" https://api.slack.com/api/auth.test`

---

## 📚 Documentação Completa

- **README.md** - Visão geral do projeto
- **SETUP.md** - Guia completo de configuração
- **QUICKSTART.md** - Este arquivo (início rápido)

---

## 🎉 Tudo Pronto!

Seu sistema está rodando! 

**Dica:** Mantenha o terminal aberto para ver os logs em tempo real.

---

**Desenvolvido para controle de estoque com metodologia 5S**

