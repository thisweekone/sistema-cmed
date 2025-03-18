"""
Script para testar a conexão e permissões do Supabase
"""
import os
from dotenv import load_dotenv
import json
from supabase import create_client
import requests
import pandas as pd
import traceback

# Carregar variáveis de ambiente
load_dotenv()

def init_supabase():
    """
    Inicializa o cliente Supabase
    """
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_KEY')
    return create_client(url, key)

def testar_ambiente():
    """
    Testa a configuração do ambiente
    """
    print("="*80)
    print("TESTANDO VARIÁVEIS DE AMBIENTE")
    print(f"SUPABASE_URL: {'✓ Definido' if os.getenv('SUPABASE_URL') else '✗ Não definido'}")
    print(f"SUPABASE_KEY: {'✓ Definido' if os.getenv('SUPABASE_KEY') else '✗ Não definido'}")
    print("="*80)

def testar_conexao():
    """
    Testa a conexão com o Supabase
    """
    print("="*80)
    print("TESTANDO CONEXÃO COM SUPABASE")
    try:
        supabase = init_supabase()
        response = supabase.table('medicamentos').select('count', count='exact').limit(1).execute()
        print(f"Conexão estabelecida com sucesso! Resposta: {response}")
        print("="*80)
        return supabase
    except Exception as e:
        print(f"ERRO ao conectar ao Supabase: {str(e)}")
        traceback.print_exc()
        print("="*80)
        return None

def verificar_tabela():
    """
    Verifica a estrutura da tabela medicamentos
    """
    print("="*80)
    print("VERIFICANDO TABELA 'medicamentos'")
    try:
        supabase = init_supabase()
        
        # Verificar se a tabela existe
        try:
            response = supabase.table('medicamentos').select('count', count='exact').execute()
            print(f"Tabela 'medicamentos' existe. Contagem: {response}")
        except Exception as e:
            print(f"Erro ao verificar tabela: {str(e)}")
            return
        
        # Tentar inserir um registro de teste
        print("\nTentando inserir registro de teste...")
        try:
            registro_teste = {
                "substancia": "TESTE DIAGNÓSTICO",
                "laboratorio": "LABORATÓRIO TESTE",
                "produto": "PRODUTO TESTE",
                "data_publicacao": "2024-03-18"
            }
            
            response = supabase.table('medicamentos').insert(registro_teste).execute()
            print(f"Registro inserido com sucesso! Resposta: {response}")
            
            # Tentar recuperar o registro inserido
            print("\nVerificando se o registro foi realmente inserido...")
            response = supabase.table('medicamentos').select('*').eq('substancia', 'TESTE DIAGNÓSTICO').execute()
            if response.data:
                print(f"Registro encontrado! Total: {len(response.data)}")
            else:
                print("ALERTA: Registro não encontrado!")
                
            # Verificar a definição da tabela
            print("\nVerificando estrutura da tabela...")
            if response.data:
                colunas = list(response.data[0].keys())
                print(f"Colunas disponíveis ({len(colunas)}): {colunas}")
            
        except Exception as e:
            print(f"Erro ao inserir registro de teste: {str(e)}")
            traceback.print_exc()
    
    except Exception as e:
        print(f"Erro ao verificar tabela: {str(e)}")
        traceback.print_exc()
    
    print("="*80)

def verificar_rls():
    """
    Verifica as políticas de segurança RLS
    """
    print("="*80)
    print("VERIFICANDO POLÍTICAS DE SEGURANÇA (RLS)")
    try:
        # Usar API REST diretamente para contornar possíveis restrições RLS
        url = f"{os.getenv('SUPABASE_URL')}/rest/v1/medicamentos?select=count"
        headers = {
            "apikey": os.getenv('SUPABASE_KEY'),
            "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
            "Content-Type": "application/json",
            "Prefer": "count=exact"
        }
        
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        # Verificar contagem via função RPC
        print("\nVerificando contagem via RPC (contorna RLS)...")
        url_rpc = f"{os.getenv('SUPABASE_URL')}/rest/v1/rpc/contar_medicamentos"
        response_rpc = requests.post(url_rpc, headers=headers)
        print(f"Status RPC: {response_rpc.status_code}")
        print(f"Resposta RPC: {response_rpc.text}")
        
    except Exception as e:
        print(f"Erro ao verificar RLS: {str(e)}")
        traceback.print_exc()
    
    print("="*80)

def verificar_permissoes():
    """
    Verifica permissões de acesso
    """
    print("="*80)
    print("VERIFICANDO PERMISSÕES DE ACESSO")
    
    try:
        # Verificar permissões via API REST
        operacoes = ["select", "insert", "update", "delete"]
        
        for op in operacoes:
            url = f"{os.getenv('SUPABASE_URL')}/rest/v1/medicamentos?limit=1"
            headers = {
                "apikey": os.getenv('SUPABASE_KEY'),
                "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
                "Content-Type": "application/json"
            }
            
            if op == "select":
                response = requests.get(url, headers=headers)
            elif op == "insert":
                # Tentativa de inserção
                test_data = {"substancia": "TESTE_PERMISSAO", "data_publicacao": "2024-03-18"}
                response = requests.post(url, headers=headers, json=test_data)
            elif op == "update":
                # Tentativa de atualização
                test_data = {"substancia": "TESTE_ATUALIZADO"}
                patch_url = f"{os.getenv('SUPABASE_URL')}/rest/v1/medicamentos?substancia=eq.TESTE_PERMISSAO"
                response = requests.patch(patch_url, headers=headers, json=test_data)
            elif op == "delete":
                # Tentativa de exclusão
                delete_url = f"{os.getenv('SUPABASE_URL')}/rest/v1/medicamentos?substancia=eq.TESTE_ATUALIZADO"
                response = requests.delete(delete_url, headers=headers)
            
            print(f"Operação {op.upper()}: Status {response.status_code}")
            
    except Exception as e:
        print(f"Erro ao verificar permissões: {str(e)}")
        traceback.print_exc()
    
    print("="*80)

def listar_registros():
    """
    Lista os registros existentes na tabela
    """
    print("="*80)
    print("LISTANDO REGISTROS EXISTENTES")
    
    try:
        supabase = init_supabase()
        
        # Obter contagem total
        response_count = supabase.table('medicamentos').select('count', count='exact').execute()
        print(f"Total de registros: {response_count.count if hasattr(response_count, 'count') else 'Desconhecido'}")
        
        # Listar os primeiros registros
        response = supabase.table('medicamentos').select('*').limit(5).execute()
        if response.data:
            print(f"\nPrimeiros {len(response.data)} registros:")
            for i, registro in enumerate(response.data):
                print(f"\nRegistro {i+1}:")
                for chave, valor in registro.items():
                    if chave in ('substancia', 'laboratorio', 'produto', 'data_publicacao'):
                        print(f"  {chave}: {valor}")
        else:
            print("\nNenhum registro encontrado!")
        
    except Exception as e:
        print(f"Erro ao listar registros: {str(e)}")
        traceback.print_exc()
    
    print("="*80)

if __name__ == "__main__":
    print("\n\n" + "="*80)
    print("DIAGNÓSTICO DO SUPABASE".center(80))
    print("="*80 + "\n")
    
    testar_ambiente()
    supabase = testar_conexao()
    if supabase:
        verificar_tabela()
        verificar_rls()
        verificar_permissoes()
        listar_registros()
    
    print("\n" + "="*80)
    print("FIM DO DIAGNÓSTICO".center(80))
    print("="*80)
