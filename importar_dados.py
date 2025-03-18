import pandas as pd
import os
import glob
from supabase import create_client
from dotenv import load_dotenv
import streamlit as st
import re
from datetime import datetime

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar conexão com Supabase
def init_connection():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos no arquivo .env")
    return create_client(url, key)

def processar_arquivo_cmed(caminho_arquivo, ano, mes=None):
    """
    Processa um arquivo da CMED e extrai os dados relevantes.
    
    Args:
        caminho_arquivo: Caminho para o arquivo Excel da CMED
        ano: Ano dos dados
        mes: Mês dos dados (opcional)
        
    Returns:
        Tuple contendo dois DataFrames: medicamentos e preços
    """
    print(f"Processando arquivo: {caminho_arquivo} - Ano: {ano}, Mês: {mes}")
    
    try:
        # Tentar diferentes abordagens para ler o arquivo, já que o formato pode variar
        try:
            df = pd.read_excel(caminho_arquivo, engine='openpyxl')
        except Exception as e:
            print(f"Erro ao ler com openpyxl: {e}")
            df = pd.read_excel(caminho_arquivo)
        
        # Normalizar nomes das colunas (remover espaços, acentos, etc.)
        df.columns = [col.lower().strip().replace(' ', '_').replace('.', '').replace('(', '').replace(')', '') 
                     for col in df.columns]
        
        print(f"Colunas encontradas: {df.columns.tolist()}")
        
        # Identificar colunas principais (podem variar entre anos)
        colunas_substancia = [col for col in df.columns if 'substancia' in col or 'principio' in col or 'ativo' in col]
        colunas_produto = [col for col in df.columns if 'produto' in col or 'medicamento' in col]
        colunas_apresentacao = [col for col in df.columns if 'apresentacao' in col]
        colunas_laboratorio = [col for col in df.columns if 'laboratorio' in col]
        colunas_classe = [col for col in df.columns if 'classe' in col and 'terapeutica' in col]
        colunas_tipo = [col for col in df.columns if 'tipo' in col and 'produto' in col]
        colunas_regime = [col for col in df.columns if 'regime' in col and 'preco' in col]
        colunas_tarja = [col for col in df.columns if 'tarja' in col]
        colunas_lista = [col for col in df.columns if 'lista' in col or 'concessao' in col]
        
        colunas_pf_sem = [col for col in df.columns if ('pf' in col or 'fabrica' in col) and 'sem' in col]
        colunas_pf_com = [col for col in df.columns if ('pf' in col or 'fabrica' in col) and 'com' in col]
        colunas_pmc_sem = [col for col in df.columns if ('pmc' in col or 'consumidor' in col) and 'sem' in col]
        colunas_pmc_com = [col for col in df.columns if ('pmc' in col or 'consumidor' in col) and 'com' in col]
        
        colunas_restricao = [col for col in df.columns if 'restric' in col or 'hospitalar' in col]
        colunas_cap = [col for col in df.columns if 'cap' in col]
        colunas_confaz = [col for col in df.columns if 'confaz' in col]
        colunas_icms0 = [col for col in df.columns if 'icms_0' in col or 'icms0' in col or 'icms_zero' in col]
        
        # Verificar se encontramos as colunas necessárias
        if not colunas_produto or not colunas_apresentacao or not colunas_laboratorio:
            print(f"Não foi possível identificar colunas essenciais. Colunas disponíveis: {df.columns.tolist()}")
            return pd.DataFrame(), pd.DataFrame()
        
        # Selecionar as primeiras colunas identificadas
        col_substancia = colunas_substancia[0] if colunas_substancia else None
        col_produto = colunas_produto[0]
        col_apresentacao = colunas_apresentacao[0]
        col_laboratorio = colunas_laboratorio[0]
        col_classe = colunas_classe[0] if colunas_classe else None
        col_tipo = colunas_tipo[0] if colunas_tipo else None
        col_regime = colunas_regime[0] if colunas_regime else None
        col_tarja = colunas_tarja[0] if colunas_tarja else None
        col_lista = colunas_lista[0] if colunas_lista else None
        
        col_pf_sem = colunas_pf_sem[0] if colunas_pf_sem else None
        col_pf_com = colunas_pf_com[0] if colunas_pf_com else None
        col_pmc_sem = colunas_pmc_sem[0] if colunas_pmc_sem else None
        col_pmc_com = colunas_pmc_com[0] if colunas_pmc_com else None
        
        col_restricao = colunas_restricao[0] if colunas_restricao else None
        col_cap = colunas_cap[0] if colunas_cap else None
        col_confaz = colunas_confaz[0] if colunas_confaz else None
        col_icms0 = colunas_icms0[0] if colunas_icms0 else None
        
        # Criar DataFrame de medicamentos
        colunas_med = []
        if col_substancia:
            colunas_med.append(col_substancia)
        colunas_med.extend([col_produto, col_apresentacao, col_laboratorio])
        if col_classe:
            colunas_med.append(col_classe)
        if col_tipo:
            colunas_med.append(col_tipo)
        if col_regime:
            colunas_med.append(col_regime)
        if col_tarja:
            colunas_med.append(col_tarja)
        if col_lista:
            colunas_med.append(col_lista)
            
        medicamentos_df = df[colunas_med].drop_duplicates()
        
        # Renomear colunas
        colunas_rename = {}
        if col_substancia:
            colunas_rename[col_substancia] = 'substancia'
        colunas_rename[col_produto] = 'produto'
        colunas_rename[col_apresentacao] = 'apresentacao'
        colunas_rename[col_laboratorio] = 'laboratorio'
        if col_classe:
            colunas_rename[col_classe] = 'classe_terapeutica'
        if col_tipo:
            colunas_rename[col_tipo] = 'tipo_produto'
        if col_regime:
            colunas_rename[col_regime] = 'regime_preco'
        if col_tarja:
            colunas_rename[col_tarja] = 'tarja'
        if col_lista:
            colunas_rename[col_lista] = 'lista_concessao'
            
        medicamentos_df = medicamentos_df.rename(columns=colunas_rename)
        
        # Gerar ID único para cada medicamento
        medicamentos_df['id'] = medicamentos_df.apply(
            lambda x: f"{x['produto']}_{x['apresentacao']}_{x['laboratorio']}".replace(' ', '_').lower(), 
            axis=1
        )
        
        # Criar DataFrame de preços
        precos_df = pd.DataFrame()
        
        # Identificar colunas de estados (ICMS)
        estados = []
        for col in df.columns:
            # Procurar por padrões como "pmc_18" ou "pf_18" que indicam alíquotas de ICMS
            match = re.search(r'(pmc|pf)_(\d+)', col)
            if match:
                aliquota = match.group(2)
                # Mapear alíquotas para estados (simplificado)
                if aliquota == '18':
                    estados.append(('SP', col))
                elif aliquota == '17':
                    estados.append(('MG', col))
                # Adicionar outros mapeamentos conforme necessário
        
        # Se não encontrou colunas de ICMS específicas, usar colunas gerais
        if not estados:
            precos_temp = df.merge(medicamentos_df, 
                                  left_on=[col_produto, col_apresentacao, col_laboratorio],
                                  right_on=['produto', 'apresentacao', 'laboratorio'])
            
            precos_temp['ano'] = ano
            precos_temp['mes'] = mes
            precos_temp['estado'] = 'BR'  # Valor padrão quando não há especificação de estado
            precos_temp['medicamento_id'] = precos_temp['id']
            
            if col_pf_sem:
                precos_temp['pf_sem_impostos'] = precos_temp[col_pf_sem]
            if col_pf_com:
                precos_temp['pf_com_impostos'] = precos_temp[col_pf_com]
            if col_pmc_sem:
                precos_temp['pmc_sem_impostos'] = precos_temp[col_pmc_sem]
            if col_pmc_com:
                precos_temp['pmc_com_impostos'] = precos_temp[col_pmc_com]
            
            if col_restricao:
                precos_temp['restricao_hospitalar'] = precos_temp[col_restricao].apply(
                    lambda x: True if isinstance(x, str) and ('sim' in x.lower() or 'hosp' in x.lower()) else False
                )
            else:
                precos_temp['restricao_hospitalar'] = False
                
            if col_cap:
                precos_temp['cap'] = precos_temp[col_cap].apply(
                    lambda x: True if isinstance(x, str) and 'sim' in x.lower() else False
                )
            else:
                precos_temp['cap'] = False
                
            if col_confaz:
                precos_temp['confaz87'] = precos_temp[col_confaz].apply(
                    lambda x: True if isinstance(x, str) and 'sim' in x.lower() else False
                )
            else:
                precos_temp['confaz87'] = False
                
            if col_icms0:
                precos_temp['icms_0'] = precos_temp[col_icms0].apply(
                    lambda x: True if isinstance(x, str) and 'sim' in x.lower() else False
                )
            else:
                precos_temp['icms_0'] = False
            
            colunas_manter = ['medicamento_id', 'ano', 'mes', 'estado']
            for col in ['pf_sem_impostos', 'pf_com_impostos', 'pmc_sem_impostos', 'pmc_com_impostos',
                       'restricao_hospitalar', 'cap', 'confaz87', 'icms_0']:
                if col in precos_temp.columns:
                    colunas_manter.append(col)
                    
            precos_df = precos_temp[colunas_manter]
        else:
            # Processar cada estado
            for estado, col_icms in estados:
                precos_temp = df.merge(medicamentos_df, 
                                      left_on=[col_produto, col_apresentacao, col_laboratorio],
                                      right_on=['produto', 'apresentacao', 'laboratorio'])
                
                precos_temp['ano'] = ano
                precos_temp['mes'] = mes
                precos_temp['estado'] = estado
                precos_temp['medicamento_id'] = precos_temp['id']
                
                # Determinar se é PMC ou PF
                if 'pmc' in col_icms.lower():
                    precos_temp['pmc_com_impostos'] = precos_temp[col_icms]
                    if col_pmc_sem:
                        precos_temp['pmc_sem_impostos'] = precos_temp[col_pmc_sem]
                    if col_pf_sem:
                        precos_temp['pf_sem_impostos'] = precos_temp[col_pf_sem]
                    if col_pf_com:
                        precos_temp['pf_com_impostos'] = precos_temp[col_pf_com]
                else:
                    precos_temp['pf_com_impostos'] = precos_temp[col_icms]
                    if col_pf_sem:
                        precos_temp['pf_sem_impostos'] = precos_temp[col_pf_sem]
                    if col_pmc_sem:
                        precos_temp['pmc_sem_impostos'] = precos_temp[col_pmc_sem]
                    if col_pmc_com:
                        precos_temp['pmc_com_impostos'] = precos_temp[col_pmc_com]
                
                if col_restricao:
                    precos_temp['restricao_hospitalar'] = precos_temp[col_restricao].apply(
                        lambda x: True if isinstance(x, str) and ('sim' in x.lower() or 'hosp' in x.lower()) else False
                    )
                else:
                    precos_temp['restricao_hospitalar'] = False
                    
                if col_cap:
                    precos_temp['cap'] = precos_temp[col_cap].apply(
                        lambda x: True if isinstance(x, str) and 'sim' in x.lower() else False
                    )
                else:
                    precos_temp['cap'] = False
                    
                if col_confaz:
                    precos_temp['confaz87'] = precos_temp[col_confaz].apply(
                        lambda x: True if isinstance(x, str) and 'sim' in x.lower() else False
                    )
                else:
                    precos_temp['confaz87'] = False
                    
                if col_icms0:
                    precos_temp['icms_0'] = precos_temp[col_icms0].apply(
                        lambda x: True if isinstance(x, str) and 'sim' in x.lower() else False
                    )
                else:
                    precos_temp['icms_0'] = False
                
                colunas_manter = ['medicamento_id', 'ano', 'mes', 'estado']
                for col in ['pf_sem_impostos', 'pf_com_impostos', 'pmc_sem_impostos', 'pmc_com_impostos',
                           'restricao_hospitalar', 'cap', 'confaz87', 'icms_0']:
                    if col in precos_temp.columns:
                        colunas_manter.append(col)
                        
                precos_df = pd.concat([precos_df, precos_temp[colunas_manter]])
        
        # Limpar dados numéricos
        for col in ['pf_sem_impostos', 'pf_com_impostos', 'pmc_sem_impostos', 'pmc_com_impostos']:
            if col in precos_df.columns:
                precos_df[col] = pd.to_numeric(precos_df[col], errors='coerce')
        
        print(f"Processado com sucesso. Medicamentos: {len(medicamentos_df)}, Preços: {len(precos_df)}")
        return medicamentos_df, precos_df
    
    except Exception as e:
        print(f"Erro ao processar arquivo {caminho_arquivo}: {e}")
        return pd.DataFrame(), pd.DataFrame()

def importar_para_supabase(medicamentos_df, precos_df):
    """
    Importa os DataFrames para o Supabase.
    
    Args:
        medicamentos_df: DataFrame com dados de medicamentos
        precos_df: DataFrame com dados de preços
    """
    try:
        supabase = init_connection()
        
        # Importar medicamentos
        if not medicamentos_df.empty:
            # Converter para lista de dicionários
            medicamentos_records = medicamentos_df.to_dict(orient='records')
            
            # Inserir no Supabase com upsert (atualizar se já existir)
            response = supabase.table("medicamentos").upsert(
                medicamentos_records, 
                on_conflict="id"
            ).execute()
            
            print(f"Medicamentos importados: {len(medicamentos_records)}")
        
        # Importar preços
        if not precos_df.empty:
            # Converter para lista de dicionários
            precos_records = precos_df.to_dict(orient='records')
            
            # Inserir no Supabase em lotes para evitar problemas com grandes volumes
            batch_size = 1000
            total_records = len(precos_records)
            
            for i in range(0, total_records, batch_size):
                batch = precos_records[i:i+batch_size]
                response = supabase.table("precos").insert(
                    batch
                ).execute()
                print(f"Lote {i//batch_size + 1}/{(total_records-1)//batch_size + 1} importado: {len(batch)} registros")
            
            print(f"Total de preços importados: {total_records}")
            
        return True
    
    except Exception as e:
        print(f"Erro ao importar para o Supabase: {e}")
        return False

def extrair_data_do_arquivo(nome_arquivo):
    """
    Tenta extrair a data (ano e mês) do nome do arquivo.
    
    Args:
        nome_arquivo: Nome do arquivo
        
    Returns:
        Tuple (ano, mes) ou (None, None) se não conseguir extrair
    """
    # Tentar extrair ano (4 dígitos)
    ano_match = re.search(r'20\d{2}', nome_arquivo)
    if ano_match:
        ano = int(ano_match.group(0))
    else:
        return None, None
    
    # Tentar extrair mês
    mes_match = re.search(r'(jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez)', nome_arquivo.lower())
    if mes_match:
        mes_str = mes_match.group(0)
        meses = {'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
                'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12}
        mes = meses.get(mes_str)
    else:
        # Tentar extrair mês numérico
        mes_num_match = re.search(r'_(\d{1,2})_', nome_arquivo)
        if mes_num_match:
            mes = int(mes_num_match.group(1))
            if mes < 1 or mes > 12:
                mes = None
        else:
            mes = None
    
    return ano, mes

def main():
    print("=== Importador de Dados CMED para Supabase ===")
    
    # Verificar se as tabelas existem no Supabase
    try:
        supabase = init_connection()
        
        # Verificar se as tabelas existem
        try:
            response = supabase.table("medicamentos").select("count", count="exact").limit(1).execute()
            print(f"Tabela 'medicamentos' existe. Registros: {response.count}")
        except Exception as e:
            print(f"Erro ao verificar tabela 'medicamentos': {e}")
            print("Você precisa criar a tabela 'medicamentos' no Supabase antes de importar os dados.")
            return
        
        try:
            response = supabase.table("precos").select("count", count="exact").limit(1).execute()
            print(f"Tabela 'precos' existe. Registros: {response.count}")
        except Exception as e:
            print(f"Erro ao verificar tabela 'precos': {e}")
            print("Você precisa criar a tabela 'precos' no Supabase antes de importar os dados.")
            return
        
    except Exception as e:
        print(f"Erro ao verificar tabelas: {e}")
        print("Você precisa criar as tabelas no Supabase antes de importar os dados.")
        print("\nCrie as seguintes tabelas:")
        print("1. medicamentos (id, substancia, produto, apresentacao, laboratorio, etc.)")
        print("2. precos (medicamento_id, ano, mes, estado, pf_sem_impostos, pf_com_impostos, etc.)")
        return
    
    # Solicitar diretório com arquivos CMED
    diretorio = input("Digite o caminho para o diretório com os arquivos CMED: ")
    
    if not os.path.exists(diretorio):
        print(f"Diretório não encontrado: {diretorio}")
        return
    
    # Encontrar arquivos Excel
    arquivos = glob.glob(os.path.join(diretorio, "*.xls*"))
    
    if not arquivos:
        print(f"Nenhum arquivo Excel encontrado em: {diretorio}")
        return
    
    print(f"Encontrados {len(arquivos)} arquivos.")
    
    # Processar cada arquivo
    for arquivo in arquivos:
        nome_arquivo = os.path.basename(arquivo)
        
        # Tentar extrair a data do nome do arquivo
        ano, mes = extrair_data_do_arquivo(nome_arquivo)
        
        if ano is None:
            try:
                ano = int(input(f"Não foi possível determinar o ano para o arquivo {nome_arquivo}. Digite o ano: "))
            except:
                print(f"Ano inválido. Pulando arquivo {nome_arquivo}.")
                continue
        
        # Perguntar se deseja processar o arquivo
        resposta = input(f"Processar arquivo {nome_arquivo} (Ano: {ano}, Mês: {mes if mes else 'N/A'})? (s/n): ")
        
        if resposta.lower() != 's':
            print(f"Pulando arquivo {nome_arquivo}.")
            continue
        
        # Processar arquivo
        medicamentos_df, precos_df = processar_arquivo_cmed(arquivo, ano, mes)
        
        if not medicamentos_df.empty and not precos_df.empty:
            # Perguntar se deseja importar
            resposta = input(f"Deseja importar os dados do arquivo {nome_arquivo} para o Supabase? (s/n): ")
            
            if resposta.lower() == 's':
                sucesso = importar_para_supabase(medicamentos_df, precos_df)
                if sucesso:
                    print(f"Dados do arquivo {nome_arquivo} importados com sucesso!")
                else:
                    print(f"Falha ao importar dados do arquivo {nome_arquivo}.")
        else:
            print(f"Não foi possível extrair dados do arquivo {nome_arquivo}.")
    
    print("Processo de importação concluído!")

if __name__ == "__main__":
    main()
