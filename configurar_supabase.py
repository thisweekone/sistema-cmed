import os
from supabase import create_client
from dotenv import load_dotenv
import time
import requests

# Carregar variáveis de ambiente
load_dotenv()

def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos no arquivo .env")
    return create_client(url, key)

def criar_tabelas():
    """
    Cria as tabelas necessárias no Supabase
    """
    print("Configurando tabelas no Supabase...")
    
    # Inicializar o cliente Supabase
    supabase = init_supabase()
    
    try:
        # Remover tabelas existentes
        print("Removendo tabelas existentes...")
        try:
            # Usar o método REST para remover tabela
            url = f"{os.getenv('SUPABASE_URL')}/rest/v1/medicamentos?select=count"
            headers = {
                "apikey": os.getenv('SUPABASE_KEY'),
                "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            # Verificar se a tabela existe
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    print("Tabela 'medicamentos' encontrada, removendo...")
                    try:
                        # Remover tabela usando REST API
                        supabase.table('medicamentos').delete().neq('id', 0).execute()
                        print("Registros da tabela 'medicamentos' removidos com sucesso")
                    except Exception as e:
                        print(f"Erro ao remover registros: {str(e)}")
                else:
                    print(f"Tabela 'medicamentos' não encontrada, status: {response.status_code}")
            except Exception as e:
                print(f"Erro ao verificar tabela: {str(e)}")
                
        except Exception as e:
            print(f"Erro ao limpar tabela 'medicamentos': {str(e)}")
    
        # Criar a tabela medicamentos
        print("Criando tabela 'medicamentos'...")
        
        # SQL para criar a tabela (via SQL direto com o cliente PostgreSQL)
        try:
            # Verificar e criar a tabela usando a API REST
            url = f"{os.getenv('SUPABASE_URL')}/rest/v1/rpc/verificar_tabela_medicamentos"
            headers = {
                "apikey": os.getenv('SUPABASE_KEY'),
                "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            
            # Enviar a requisição para criar a tabela
            response = requests.post(url, headers=headers, json={})
            print(f"Resposta da verificação da tabela: {response.text}")
            
            print("Verificar a estrutura da tabela...")
            
            # Inserir um registro de teste para verificar a estrutura da tabela
            teste_registro = {
                "substancia": "TESTE CONFIGURAÇÃO",
                "cnpj": "12345678901234",
                "laboratorio": "LABORATÓRIO TESTE",
                "codigo_ggrem": "1234567890123",
                "registro": "1234567890",
                "ean_1": "1234567890123",
                "ean_2": "1234567890123",
                "ean_3": "1234567890123",
                "produto": "MEDICAMENTO TESTE",
                "apresentacao": "APRESENTAÇÃO TESTE",
                "classe_terapeutica": "CLASSE TESTE",
                "tipo_de_produto": "TIPO TESTE",
                "regime_de_preco": "REGIME TESTE",
                "pf_sem_impostos": 100.00,
                "data_publicacao": "2024-03-18"
            }
            
            # Tentar inserir o registro de teste
            teste_response = supabase.table('medicamentos').insert(teste_registro).execute()
            print(f"Inserção de teste realizada: {teste_response}")
            
        except Exception as e:
            print(f"Erro ao verificar a estrutura da tabela: {str(e)}")
        
        print("Configuração das tabelas concluída!")
    
    except Exception as e:
        print(f"Erro durante a configuração das tabelas: {str(e)}")

if __name__ == "__main__":
    criar_tabelas()
