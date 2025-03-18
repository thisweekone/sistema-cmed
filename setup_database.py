import os
from supabase import create_client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def init_connection():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos no arquivo .env")
    return create_client(url, key)

def criar_tabelas():
    """
    Cria as tabelas necessárias no Supabase.
    Nota: Este script é apenas um auxiliar. O Supabase não permite
    criar tabelas via API, então você precisará criar manualmente
    no painel do Supabase.
    """
    print("=== Script de Configuração do Banco de Dados Supabase ===")
    print("\nInstruções para criar as tabelas no Supabase:")
    
    print("\n1. Acesse o painel do Supabase: https://app.supabase.io")
    print("2. Selecione seu projeto")
    print("3. Vá para a seção 'Table Editor'")
    
    print("\n4. Crie a tabela 'medicamentos' com as seguintes colunas:")
    print("   - id (text, primary key)")
    print("   - substancia (text)")
    print("   - produto (text, not null)")
    print("   - apresentacao (text, not null)")
    print("   - laboratorio (text, not null)")
    print("   - classe_terapeutica (text)")
    print("   - tipo_produto (text)")
    print("   - regime_preco (text)")
    print("   - tarja (text)")
    print("   - lista_concessao (text)")
    
    print("\n5. Crie a tabela 'precos' com as seguintes colunas:")
    print("   - id (uuid, primary key, default: uuid_generate_v4())")
    print("   - medicamento_id (text, not null, foreign key -> medicamentos.id)")
    print("   - ano (integer, not null)")
    print("   - mes (integer)")
    print("   - estado (text, not null)")
    print("   - pf_sem_impostos (numeric)")
    print("   - pf_com_impostos (numeric)")
    print("   - pmc_sem_impostos (numeric)")
    print("   - pmc_com_impostos (numeric)")
    print("   - restricao_hospitalar (boolean, default: false)")
    print("   - cap (boolean, default: false)")
    print("   - confaz87 (boolean, default: false)")
    print("   - icms_0 (boolean, default: false)")
    
    print("\n6. Crie um índice composto na tabela 'precos' para evitar duplicatas:")
    print("   - Colunas: medicamento_id, ano, mes, estado")
    print("   - Tipo: unique")
    
    print("\nOpcionalmente, você pode criar uma política de acesso público para leitura:")
    print("1. Vá para a seção 'Authentication' -> 'Policies'")
    print("2. Para cada tabela, adicione uma política que permita SELECT para todos")
    
    # Verificar conexão com o Supabase
    try:
        supabase = init_connection()
        print("\nConexão com o Supabase estabelecida com sucesso!")
        
        # Verificar se as tabelas já existem
        try:
            response = supabase.table("medicamentos").select("count", count="exact").limit(1).execute()
            print(f"Tabela 'medicamentos' já existe. Registros: {response.count}")
        except:
            print("Tabela 'medicamentos' não encontrada. Siga as instruções acima para criá-la.")
        
        try:
            response = supabase.table("precos").select("count", count="exact").limit(1).execute()
            print(f"Tabela 'precos' já existe. Registros: {response.count}")
        except:
            print("Tabela 'precos' não encontrada. Siga as instruções acima para criá-la.")
            
    except Exception as e:
        print(f"\nErro ao conectar ao Supabase: {e}")
        print("Verifique suas credenciais no arquivo .env")

if __name__ == "__main__":
    criar_tabelas()
