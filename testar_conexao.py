import os
from supabase import create_client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def testar_conexao():
    """
    Testa a conexão com o Supabase e exibe informações básicas sobre as tabelas.
    """
    print("=== Teste de Conexão com o Supabase ===")
    
    # Verificar se as variáveis de ambiente estão configuradas
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("Erro: SUPABASE_URL e/ou SUPABASE_KEY não estão definidos no arquivo .env")
        print("Por favor, configure o arquivo .env com suas credenciais do Supabase.")
        return
    
    # Tentar conectar ao Supabase
    try:
        print("Conectando ao Supabase...")
        supabase = create_client(url, key)
        
        # Testar tabela de medicamentos
        try:
            response = supabase.table("medicamentos").select("count", count="exact").limit(1).execute()
            print(f"✅ Tabela 'medicamentos' acessível. Total de registros: {response.count}")
            
            # Mostrar alguns medicamentos de exemplo
            if response.count > 0:
                exemplos = supabase.table("medicamentos").select("*").limit(5).execute()
                print(f"\nExemplos de medicamentos ({min(5, len(exemplos.data))} de {response.count}):")
                for med in exemplos.data:
                    print(f"  - {med.get('nome')} - {med.get('apresentacao')} ({med.get('laboratorio')})")
        except Exception as e:
            print(f"❌ Erro ao acessar tabela 'medicamentos': {e}")
        
        # Testar tabela de preços
        try:
            response = supabase.table("precos").select("count", count="exact").limit(1).execute()
            print(f"✅ Tabela 'precos' acessível. Total de registros: {response.count}")
            
            # Mostrar anos disponíveis
            if response.count > 0:
                anos = supabase.table("precos").select("ano").distinct().execute()
                anos_disponiveis = sorted(set(item.get('ano') for item in anos.data))
                print(f"\nAnos disponíveis: {anos_disponiveis}")
                
                # Mostrar estados disponíveis
                estados = supabase.table("precos").select("estado").distinct().execute()
                estados_disponiveis = sorted(set(item.get('estado') for item in estados.data))
                print(f"Estados disponíveis: {estados_disponiveis}")
        except Exception as e:
            print(f"❌ Erro ao acessar tabela 'precos': {e}")
        
        print("\n✅ Teste de conexão concluído com sucesso!")
        print("Você pode executar a aplicação com: streamlit run app.py")
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao Supabase: {e}")
        print("Verifique se suas credenciais estão corretas no arquivo .env")

if __name__ == "__main__":
    testar_conexao()
