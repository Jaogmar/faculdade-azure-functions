import logging
import os
from datetime import datetime, timezone

import azure.functions as func
import requests

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.timer_trigger(
    schedule="0 */1 * * * *",
    arg_name="timer",
    run_on_startup=False,
    use_monitor=False,
)
def timer_log(timer: func.TimerRequest) -> None:
    if timer.past_due:
        logging.warning("execucao atrasada (past due)")

    agora = datetime.now(timezone.utc).isoformat()
    logging.info("Ola do timer trigger! Executado em %s (UTC)", agora)


@app.route(route="echo", methods=["GET"])
def echo(req: func.HttpRequest) -> func.HttpResponse:
    mensagem = req.params.get("mensagem")

    if not mensagem:
        logging.warning("chamada sem o parametro 'mensagem'")
        return func.HttpResponse(
            "Informe o parametro na URL. Exemplo: /api/echo?mensagem=ola",
            status_code=400,
            mimetype="text/plain",
        )

    logging.info("parametro recebido: %s", mensagem)
    return func.HttpResponse(
        f"TAPRB-2026 Parametro recebido: {mensagem}",
        status_code=200,
        mimetype="text/plain",
    )


@app.timer_trigger(
    schedule="0 */2 * * * *",
    arg_name="timer",
    run_on_startup=True,
    use_monitor=False,
)
def timer_chama_http(timer: func.TimerRequest) -> None:
    if timer.past_due:
        logging.warning("execucao atrasada (past due)")

    url = os.environ.get("TARGET_FUNCTION_URL", "http://localhost:7071/api/echo")
    mensagem = f"ping-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    logging.info("chamando %s com mensagem=%s", url, mensagem)

    try:
        resposta = requests.get(url, params={"mensagem": mensagem}, timeout=10)
    except requests.RequestException as erro:
        logging.error("falha ao chamar %s: %s", url, erro)
        return

    logging.info(
        "status=%s resposta=%s",
        resposta.status_code,
        resposta.text,
    )
