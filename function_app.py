import logging
import azure.functions as func
import os
import pyodbc

app = func.FunctionApp()

@app.timer_trigger(schedule="0 * * * * *", arg_name="myTimer", run_on_startup=False,
              use_monitor=False) 
def extract_chamado(myTimer: func.TimerRequest) -> None:

    host = os.getenv("HOST")
    database = os.getenv("DATABASE")
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")


    #criar a conexao com o banco de dados
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={host};"
        f"DATABASE={database};"
        f"UID={user};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    
    #Estabelece a conexão com o banco de dados usando pyodbc
    #fazer select na tabela itsm.chamado
    #exibir os dados na tela
    
    logging.info("Iniciando a extração de dados do banco de dados...")
    
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        logging.info("Conexão com o banco de dados estabelecida com sucesso.")
        
        # Executar a consulta SQL para extrair os dados
        query = "SELECT  s.name AS schema_name, t.name AS table_name FROM sys.tables AS t INNER JOIN sys.schemas AS s ON t.schema_id = s.schema_id ORDER BY s.name, t.name;"
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Processar os resultados
        for row in rows:
            logging.info(f"Chamado ID: {row[0]}, Descrição: {row[1]}") 
    except pyodbc.Error as e:
        logging.error(f"Erro ao conectar ao banco de dados: {e}")
    logging.info("Extração de dados concluída com sucesso.")   
