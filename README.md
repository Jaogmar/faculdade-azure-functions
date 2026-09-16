# Projeto de Estudos da Faculdadade

Projeto da faculdade explorando as Azure Functions desenvolvidas em **Python**.

## Integrantes da equipe

| Nome |
| --- |
| João Gabriel |
| Thiogo Antônio |
| Luiz Chaves |
| Arthur Luckman |
| Gabriel Fagundes |

## Functions

Todas as functions estão em [`function_app.py`](function_app.py).

| Function | Gatilho | Configuração | O que faz |
| --- | --- | --- | --- |
| `timer_log` | Timer trigger | `0 */1 * * * *` (a cada 1 minuto) | Imprime apenas um log no terminal com o horário da execução. |
| `echo` | HTTP trigger (GET) | rota `/api/echo`, auth anônima | Recebe o parâmetro `mensagem` pela URL e o imprime na tela, prefixado pelo texto identificador `TAPRB-2026 Parametro recebido:`. |
| `timer_chama_http` | Timer trigger | `0 */2 * * * *` (a cada 2 minutos) | Faz uma chamada HTTP GET para a function `echo`, enviando uma mensagem gerada, e registra no log a resposta devolvida. |

A URL chamada por `timer_chama_http` é resolvida em três níveis, nesta ordem:

1. app setting **`TARGET_FUNCTION_URL`**, se estiver definida — permite apontar para qualquer outro Function App sem alterar o código;
2. senão, é montado a partir de **`WEBSITE_HOSTNAME`**, variável que o Azure injeta automaticamente no Function App (`https://<seu-app>.azurewebsites.net`) — ou seja, depois de publicar não é preciso configurar nada;
3. senão, `http://localhost:7071`, para execução local.

A função `build_domain()` devolve apenas o domínio; a rota (`/api/echo`) é concatenada por quem chama.

## Pré-requisitos

- [Azure Functions Core Tools v4](https://learn.microsoft.com/azure/azure-functions/functions-run-local): `npm i -g azure-functions-core-tools@4 --unsafe-perm true`
- Python **3.11 ou 3.12** (versões com suporte estável no worker Python do Azure Functions)
- [Azurite](https://learn.microsoft.com/azure/storage/common/storage-use-azurite) para o storage local exigido pelos timer triggers: `npx azurite --silent`

