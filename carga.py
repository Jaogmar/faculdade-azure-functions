import json
import logging
import os

import pyodbc
from azure.core.exceptions import AzureError

logger = logging.getLogger(__name__)

VARIAVEIS_DESTINO = ("DEST_DB_HOST", "DEST_DB_NAME", "DEST_DB_USER", "DEST_DB_PASSWORD")

# Ordem respeita as chaves estrangeiras: pais antes dos filhos
ORDEM_CARGA = (
    ("categoria", "id_categoria"),
    ("cliente_organizacao", "id_cliente_organizacao"),
    ("fila", "id_fila"),
    ("sla", "id_sla"),
    ("analista", "id_analista"),
    ("solicitante", "id_solicitante"),
    ("chamado", "id_chamado"),
    ("chamado_sla", "id_chamado_sla"),
    ("chamado_status_historico", "id_chamado_status_historico"),
    ("csat_avaliacao", "id_csat_avaliacao"),
)


def conectar_destino() -> pyodbc.Connection:
    faltando = [n for n in VARIAVEIS_DESTINO if not os.getenv(n)]
    if faltando:
        raise RuntimeError(
            f"Variaveis de ambiente nao configuradas: {', '.join(faltando)}"
        )
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={os.environ['DEST_DB_HOST']};"
        f"DATABASE={os.environ['DEST_DB_NAME']};"
        f"UID={os.environ['DEST_DB_USER']};"
        f"PWD={os.environ['DEST_DB_PASSWORD']};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)


def ler_ultimo_bronze(container, fonte: str, entidade: str) -> list[dict]:
    prefixo = f"{fonte}/{entidade}/"
    nomes = [b.name for b in container.list_blobs(name_starts_with=prefixo)]
    if not nomes:
        return []
    # ano=/mes=/dia= + timestamp no nome: ordem lexicografica = ordem cronologica
    dados = container.download_blob(max(nomes)).readall()
    return json.loads(dados.decode("utf-8"))


def _colunas_destino(cursor, tabela: str) -> set[str]:
    cursor.execute(
        "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = ?",
        tabela,
    )
    return {r[0] for r in cursor.fetchall()}


def upsert_tabela(cursor, tabela: str, pk: str, registros: list[dict]) -> int:
    if not registros:
        return 0
    colunas_dest = _colunas_destino(cursor, tabela)
    colunas = [c for c in registros[0] if c in colunas_dest]
    if pk not in colunas:
        raise RuntimeError(f"Chave {pk} ausente nos dados de {tabela}")

    lista = ", ".join(colunas)
    origem = ", ".join(f"s.{c}" for c in colunas)
    marcadores = ", ".join("?" for _ in colunas)
    sets = ", ".join(f"t.{c} = s.{c}" for c in colunas if c != pk)
    sql = (
        f"MERGE dbo.{tabela} AS t "
        f"USING (VALUES ({marcadores})) AS s ({lista}) ON t.{pk} = s.{pk} "
        f"WHEN MATCHED THEN UPDATE SET {sets} "
        f"WHEN NOT MATCHED THEN INSERT ({lista}) VALUES ({origem});"
    )
    linhas = [tuple(r.get(c) for c in colunas) for r in registros]

    cursor.execute(f"SET IDENTITY_INSERT dbo.{tabela} ON;")
    for linha in linhas:
        cursor.execute(sql, linha)
    cursor.execute(f"SET IDENTITY_INSERT dbo.{tabela} OFF;")
    return len(linhas)


def popular_tabelas(container, fonte: str) -> None:
    try:
        conn = conectar_destino()
    except RuntimeError as e:
        logger.error(str(e))
        return
    except pyodbc.Error as e:
        logger.error(f"Erro ao conectar ao banco de destino: {e}")
        return

    try:
        cursor = conn.cursor()
        for tabela, pk in ORDEM_CARGA:
            try:
                registros = ler_ultimo_bronze(container, fonte, tabela)
            except AzureError as e:
                logger.error(f"Erro ao ler {tabela} do bronze: {e}")
                conn.rollback()
                return
            total = upsert_tabela(cursor, tabela, pk, registros)
            logger.info(f"dbo.{tabela}: {total} registros carregados.")
        conn.commit()
    except (pyodbc.Error, RuntimeError) as e:
        conn.rollback()
        logger.error(f"Erro na carga do destino, transacao revertida: {e}")
    finally:
        conn.close()
