import json
import logging
import os

import azure.functions as func
import pyodbc

app = func.FunctionApp()

VARIAVEIS_BANCO = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD")
AGENDAMENTO = "0 */5 * * * *"  # a cada 5 minutos


def _get_connection() -> pyodbc.Connection:
    # As credenciais vem apenas das variaveis de ambiente
    # (local.settings.json localmente / Application settings no Azure)
    faltando = [nome for nome in VARIAVEIS_BANCO if not os.getenv(nome)]
    if faltando:
        raise RuntimeError(f"Variaveis de ambiente nao configuradas: {', '.join(faltando)}")

    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={os.environ['DB_HOST']};"
        f"DATABASE={os.environ['DB_NAME']};"
        f"UID={os.environ['DB_USER']};"
        f"PWD={os.environ['DB_PASSWORD']};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)


def _extrair_tabela(nome_tabela: str) -> None:
    # O nome da tabela vem fixo de cada function
    logging.info(f"Iniciando a extração da tabela itsm.{nome_tabela}...")

    try:
        conn = _get_connection()
    except RuntimeError as e:
        logging.error(str(e))
        return
    except pyodbc.Error as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
        return

    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM itsm.{nome_tabela};")
        colunas = [coluna[0] for coluna in cursor.description]
        rows = cursor.fetchall()
    except pyodbc.Error as e:
        logging.error(f"Erro ao extrair a tabela itsm.{nome_tabela}: {e}")
        return
    finally:
        conn.close()

    for row in rows:
        registro = dict(zip(colunas, row))
        logging.info(f"itsm.{nome_tabela}: {json.dumps(registro, default=str, ensure_ascii=False)}")

    logging.info(f"Extração da tabela itsm.{nome_tabela} concluída: {len(rows)} registros.")


@app.timer_trigger(schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_analista(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("analista")


@app.timer_trigger(schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_categoria(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("categoria")


@app.timer_trigger(schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_chamado(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("chamado")


@app.timer_trigger(schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_chamado_sla(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("chamado_sla")


@app.timer_trigger(schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_chamado_status_historico(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("chamado_status_historico")


@app.timer_trigger(schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_cliente_organizacao(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("cliente_organizacao")


@app.timer_trigger(schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_csat_avaliacao(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("csat_avaliacao")


@app.timer_trigger(schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_fila(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("fila")


@app.timer_trigger(schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_sla(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("sla")


@app.timer_trigger(schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def extract_solicitante(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("solicitante")
