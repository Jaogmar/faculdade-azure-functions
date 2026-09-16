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
