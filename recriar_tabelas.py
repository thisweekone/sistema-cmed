import os
import psycopg2
from dotenv import load_dotenv
from urllib.parse import urlparse

def get_db_connection():
    """Obtém uma conexão direta com o banco de dados do Supabase"""
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Obter URL do banco de dados do Supabase
    db_url = os.getenv("SUPABASE_DB_URL")
    if not db_url:
        raise ValueError("SUPABASE_DB_URL deve ser definida no arquivo .env")
    
    # Conectar ao banco de dados
    print("Conectando ao banco de dados...")
    conn = psycopg2.connect(db_url)
    return conn

def executar_sql_arquivo(caminho_arquivo):
    """Executa o SQL do arquivo especificado"""
    # Ler o conteúdo do arquivo SQL
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print(f"Executando SQL do arquivo: {caminho_arquivo}")
    print("="*50)
    print(sql)
    print("="*50)
    
    try:
        # Conectar ao banco de dados
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Executar o SQL
        cur.execute(sql)
        
        # Commit das alterações
        conn.commit()
        
        print("SQL executado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao executar SQL: {str(e)}")
        raise
    finally:
        # Fechar conexão
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Executar o script SQL
    executar_sql_arquivo('recriar_tabelas.sql')
