import os
from dotenv import load_dotenv
from supabase import create_client

# Carregar variáveis de ambiente
load_dotenv()

def main():
    # Obter variáveis de ambiente
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    print(f"SUPABASE_URL definido: {'Sim' if url else 'Não'}")
    print(f"SUPABASE_KEY definido: {'Sim' if key else 'Não'}")
    
    if not url or not key:
        print("Erro: SUPABASE_URL e SUPABASE_KEY devem ser definidos no arquivo .env")
        return
    
    try:
        # Inicializar conexão
        print("Tentando conectar ao Supabase...")
        supabase = create_client(url, key)
        
        # Testar conexão com tabela medicamentos
        print("Verificando tabela 'medicamentos'...")
        response = supabase.table("medicamentos").select("count", count="exact").limit(1).execute()
        print(f"Tabela 'medicamentos' encontrada. Registros: {response.count}")
        
        # Testar conexão com tabela precos
        print("Verificando tabela 'precos'...")
        response = supabase.table("precos").select("count", count="exact").limit(1).execute()
        print(f"Tabela 'precos' encontrada. Registros: {response.count}")
        
        print("Conexão com Supabase estabelecida com sucesso!")
    except Exception as e:
        print(f"Erro ao conectar ao Supabase: {e}")

if __name__ == "__main__":
    main()
