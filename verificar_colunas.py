import os
from supabase import create_client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos no arquivo .env")
    return create_client(url, key)

def verificar_colunas():
    try:
        supabase = init_supabase()
        
        # Verificar se a coluna data_publicacao existe na tabela medicamentos
        try:
            # Tentar adicionar a coluna se não existir
            supabase.table("medicamentos").select("data_publicacao").limit(1).execute()
            print("✅ Coluna 'data_publicacao' já existe na tabela 'medicamentos'")
        except Exception as e:
            if "column" in str(e) and "does not exist" in str(e):
                print("❌ Coluna 'data_publicacao' não existe na tabela 'medicamentos'")
                print("Adicionando coluna 'data_publicacao' à tabela 'medicamentos'...")
                
                # SQL para adicionar a coluna
                sql = """
                ALTER TABLE medicamentos 
                ADD COLUMN IF NOT EXISTS data_publicacao DATE;
                """
                
                try:
                    supabase.rpc("exec_sql", {"query": sql}).execute()
                    print("✅ Coluna 'data_publicacao' adicionada com sucesso à tabela 'medicamentos'")
                except Exception as e:
                    print(f"❌ Erro ao adicionar coluna: {str(e)}")
            else:
                print(f"❌ Erro ao verificar coluna: {str(e)}")
        
        # Verificar se a coluna data_publicacao existe na tabela precos
        try:
            # Tentar adicionar a coluna se não existir
            supabase.table("precos").select("data_publicacao").limit(1).execute()
            print("✅ Coluna 'data_publicacao' já existe na tabela 'precos'")
        except Exception as e:
            if "column" in str(e) and "does not exist" in str(e):
                print("❌ Coluna 'data_publicacao' não existe na tabela 'precos'")
                print("Adicionando coluna 'data_publicacao' à tabela 'precos'...")
                
                # SQL para adicionar a coluna
                sql = """
                ALTER TABLE precos 
                ADD COLUMN IF NOT EXISTS data_publicacao DATE;
                """
                
                try:
                    supabase.rpc("exec_sql", {"query": sql}).execute()
                    print("✅ Coluna 'data_publicacao' adicionada com sucesso à tabela 'precos'")
                except Exception as e:
                    print(f"❌ Erro ao adicionar coluna: {str(e)}")
            else:
                print(f"❌ Erro ao verificar coluna: {str(e)}")
    
    except Exception as e:
        import traceback
        print(f"Erro ao verificar colunas: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    verificar_colunas()
