import json
import logging
import os
from datetime import UTC, datetime

import azure.functions as func
import pyodbc
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)

app = func.FunctionApp()

VARIAVEIS_BANCO = ("DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD")
AGENDAMENTO = "0 */5 * * * *"  # a cada 5 minutos

CONTAINER_BRONZE = "bronze"
FONTE = "itsm"


def _get_connection() -> pyodbc.Connection:
    # As credenciais vem apenas das variaveis de ambiente
    # (local.settings.json localmente / Application settings no Azure)
    faltando = [nome for nome in VARIAVEIS_BANCO if not os.getenv(nome)]
    if faltando:
        raise RuntimeError(
            f"Variaveis de ambiente nao configuradas: {', '.join(faltando)}"
        )

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


def _get_container_client():
    # Conta do Data Lake: connection string (DATALAKE_CONNECTION_STRING) ou
    # URL da conta + identidade gerenciada (DATALAKE_ACCOUNT_URL)
    conn_str = os.getenv("DATALAKE_CONNECTION_STRING")
    if conn_str:
        service = BlobServiceClient.from_connection_string(conn_str)
    else:
        account_url = os.getenv("DATALAKE_ACCOUNT_URL")
        if not account_url:
            raise RuntimeError(
                "Configure DATALAKE_CONNECTION_STRING ou DATALAKE_ACCOUNT_URL"
            )
        from azure.identity import DefaultAzureCredential

        service = BlobServiceClient(account_url, credential=DefaultAzureCredential())
    return service.get_container_client(CONTAINER_BRONZE)


def _caminho_blob(entidade: str, agora: datetime) -> str:
    # bronze/itsm/<entidade>/ano=YYYY/mes=MM/dia=DD/<entidade>_YYYYMMDDTHHMMSSZ.json
    return (
        f"{FONTE}/{entidade}/"
        f"ano={agora:%Y}/mes={agora:%m}/dia={agora:%d}/"
        f"{entidade}_{agora:%Y%m%dT%H%M%SZ}.json"
    )


def _salvar_bronze(nome_tabela: str, registros: list[dict]) -> str:
    agora = datetime.now(UTC)
    caminho = _caminho_blob(nome_tabela, agora)
    conteudo = json.dumps(registros, default=str, ensure_ascii=False)
    _get_container_client().upload_blob(
        name=caminho, data=conteudo.encode("utf-8"), overwrite=True
    )
    return caminho


def _extrair_tabela(nome_tabela: str) -> None:
    # O nome da tabela vem fixo de cada function
    logger.info(f"Iniciando a extração da tabela itsm.{nome_tabela}...")

    try:
        conn = _get_connection()
    except RuntimeError as e:
        logger.error(str(e))
        return
    except pyodbc.Error as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        return

    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM itsm.{nome_tabela};")
        colunas = [coluna[0] for coluna in cursor.description]
        rows = cursor.fetchall()
    except pyodbc.Error as e:
        logger.error(f"Erro ao extrair a tabela itsm.{nome_tabela}: {e}")
        return
    finally:
        conn.close()

    registros = [dict(zip(colunas, row)) for row in rows]

    try:
        caminho = _salvar_bronze(nome_tabela, registros)
    except (RuntimeError, AzureError) as e:
        logger.error(f"Erro ao salvar itsm.{nome_tabela} no container bronze: {e}")
        return

    logger.info(
        f"Extração da tabela itsm.{nome_tabela} concluída: "
        f"{len(registros)} registros salvos em {CONTAINER_BRONZE}/{caminho}."
    )


@app.timer_trigger(
    schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_analista(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("analista")


@app.timer_trigger(
    schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_categoria(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("categoria")


@app.timer_trigger(
    schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_chamado(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("chamado")


@app.timer_trigger(
    schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_chamado_sla(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("chamado_sla")


@app.timer_trigger(
    schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_chamado_status_historico(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("chamado_status_historico")


@app.timer_trigger(
    schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_cliente_organizacao(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("cliente_organizacao")


@app.timer_trigger(
    schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_csat_avaliacao(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("csat_avaliacao")


@app.timer_trigger(
    schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_fila(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("fila")


@app.timer_trigger(
    schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_sla(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("sla")


@app.timer_trigger(
    schedule=AGENDAMENTO, arg_name="myTimer", run_on_startup=False, use_monitor=False
)
def extract_solicitante(myTimer: func.TimerRequest) -> None:
    _extrair_tabela("solicitante")
