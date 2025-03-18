import os
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd

# Carregar variáveis de ambiente
load_dotenv()

def init_connection():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos no arquivo .env")
    return create_client(url, key)

def verificar_conexao():
    print("=== Verificação de Conexão com o Supabase ===")
    
    try:
        supabase = init_connection()
        print("✅ Conexão com o Supabase estabelecida com sucesso!")
        
        # Verificar tabela medicamentos
        try:
            response = supabase.table("medicamentos").select("count", count="exact").limit(1).execute()
            print(f"✅ Tabela 'medicamentos' encontrada. Registros: {response.count}")
            
            # Verificar colunas
            try:
                response = supabase.table("medicamentos").select("*").limit(1).execute()
                if response.data:
                    colunas = list(response.data[0].keys())
                    print(f"   Colunas encontradas: {colunas}")
                else:
                    print("   Tabela 'medicamentos' está vazia.")
            except Exception as e:
                print(f"   Erro ao verificar colunas: {e}")
                
        except Exception as e:
            print(f"❌ Tabela 'medicamentos' não encontrada ou erro de acesso: {e}")
            print("   Você precisa criar esta tabela manualmente no painel do Supabase.")
        
        # Verificar tabela precos
        try:
            response = supabase.table("precos").select("count", count="exact").limit(1).execute()
            print(f"✅ Tabela 'precos' encontrada. Registros: {response.count}")
            
            # Verificar colunas
            try:
                response = supabase.table("precos").select("*").limit(1).execute()
                if response.data:
                    colunas = list(response.data[0].keys())
                    print(f"   Colunas encontradas: {colunas}")
                else:
                    print("   Tabela 'precos' está vazia.")
            except Exception as e:
                print(f"   Erro ao verificar colunas: {e}")
                
        except Exception as e:
            print(f"❌ Tabela 'precos' não encontrada ou erro de acesso: {e}")
            print("   Você precisa criar esta tabela manualmente no painel do Supabase.")
            
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {e}")
        print("   Verifique suas credenciais no arquivo .env")
    
    print("\n=== Próximos Passos ===")
    print("1. Se as tabelas não existirem, crie-as manualmente no painel do Supabase")
    print("2. Execute o script setup_database.py para ver as instruções detalhadas")
    print("3. Após criar as tabelas, execute importar_dados.py para importar dados da CMED")
    print("4. Execute streamlit run app.py para iniciar o aplicativo")

if __name__ == "__main__":
    verificar_conexao()
