# TAPRB-2026

Projeto da disciplina **TAPRB** contendo Azure Functions desenvolvidas em **Python (modelo de programação v2)**.

## Integrantes da equipe

| Nome | GitHub |
| --- | --- |
| João Gabriel | `@preencher` |
| Thiogo Antônio | `@preencher` |
| Luiz Chaves | `@preencher` |
| Arthur Luckman | `@preencher` |
| Gabriel Fagundes | `@preencher` |

## Functions

Todas as functions estão em [`function_app.py`](function_app.py).

| Function | Gatilho | Configuração | O que faz |
| --- | --- | --- | --- |
| `timer_log` | Timer trigger | `0 */1 * * * *` (a cada 1 minuto) | Imprime apenas um log no terminal com o horário da execução. |
| `echo` | HTTP trigger (GET) | rota `/api/echo`, auth anônima | Recebe o parâmetro `mensagem` pela URL e o imprime na tela, prefixado pelo texto identificador `TAPRB-2026 Parametro recebido:`. |
| `timer_chama_http` | Timer trigger | `0 */2 * * * *` (a cada 2 minutos) | Faz uma chamada HTTP GET para a function `echo`, enviando uma mensagem gerada, e registra no log a resposta devolvida. |

A URL chamada por `timer_chama_http` vem da app setting **`TARGET_FUNCTION_URL`**; se ela não estiver definida, o padrão é `http://localhost:7071/api/echo`.

## Pré-requisitos

- [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local): `npm i -g azure-functions-core-tools@4 --unsafe-perm true`
- Python **3.11 ou 3.12** (versões com suporte estável no worker Python do Azure Functions)
- [Azurite](https://learn.microsoft.com/azure/storage/common/storage-use-azurite) para o storage local exigido pelos timer triggers: `npx azurite --silent`

## Como executar localmente

```bash
# 1. criar e ativar o ambiente virtual
python -m venv .venv
.venv\Scripts\activate        # Windows (PowerShell/CMD)
# source .venv/bin/activate   # Linux/macOS

# 2. instalar as dependências
pip install -r requirements.txt

# 3. copiar as configurações locais
copy local.settings.json.example local.settings.json   # Windows
# cp local.settings.json.example local.settings.json   # Linux/macOS

# 4. em um terminal separado, subir o Azurite
npx azurite --silent

# 5. iniciar o runtime das functions
func start
```

## Exemplo de uso

```bash
curl "http://localhost:7071/api/echo?mensagem=ola"
```

Resposta:

```
TAPRB-2026 Parametro recebido: ola
```

No terminal do `func start` também aparecem, periodicamente:

```
Ola do timer trigger! Executado em 2026-09-15T21:40:00+00:00 (UTC)
Chamando http://localhost:7071/api/echo com mensagem=ping-20260915214000
Status=200 resposta=TAPRB-2026 Parametro recebido: ping-20260915214000
```

## Publicação no GitHub

1. Crie no GitHub um repositório **público** chamado `TAPRB-2026` (sem README, para não gerar conflito).
2. Na pasta do projeto:

```bash
git init
git add .
git commit -m "Projeto TAPRB-2026 com Azure Functions"
git branch -M main
git remote add origin https://github.com/<seu-usuario>/TAPRB-2026.git
git push -u origin main
```

3. Compartilhe com a equipe em **Settings → Collaborators → Add people**, convidando os demais integrantes.

## Publicação no Azure (opcional)

```bash
func azure functionapp publish <nome-do-function-app>
```

Depois de publicar, defina a app setting `TARGET_FUNCTION_URL` apontando para a URL pública da function `echo`:

```bash
az functionapp config appsettings set \
  --name <nome-do-function-app> \
  --resource-group <grupo-de-recursos> \
  --settings TARGET_FUNCTION_URL="https://<nome-do-function-app>.azurewebsites.net/api/echo"
```
