import pandas as pd
import os
from importar_dados import processar_arquivo_cmed, extrair_data_do_arquivo

def testar_processamento_arquivo():
    """
    Testa o processamento de um arquivo CMED sem importar para o Supabase.
    Útil para verificar se o script consegue extrair corretamente os dados.
    """
    print("=== Teste de Processamento de Arquivo CMED ===")
    
    # Solicitar caminho do arquivo
    caminho_arquivo = input("Digite o caminho completo para o arquivo Excel da CMED: ")
    
    if not os.path.exists(caminho_arquivo):
        print(f"Erro: O arquivo {caminho_arquivo} não existe.")
        return
    
    # Extrair ano e mês do nome do arquivo
    nome_arquivo = os.path.basename(caminho_arquivo)
    ano, mes = extrair_data_do_arquivo(nome_arquivo)
    
    if not ano:
        # Se não conseguiu extrair do nome, solicitar ao usuário
        ano = int(input("Digite o ano dos dados (ex: 2023): "))
        mes = input("Digite o mês dos dados (opcional, 1-12): ")
        if mes:
            mes = int(mes)
        else:
            mes = None
    
    print(f"Processando arquivo {nome_arquivo} - Ano: {ano}, Mês: {mes}")
    
    # Processar o arquivo
    medicamentos_df, precos_df = processar_arquivo_cmed(caminho_arquivo, ano, mes)
    
    # Verificar resultados
    if medicamentos_df.empty:
        print("Erro: Não foi possível extrair dados de medicamentos do arquivo.")
    else:
        print(f"\n✅ Extraídos {len(medicamentos_df)} medicamentos")
        print("\nColunas encontradas em medicamentos:")
        for col in medicamentos_df.columns:
            print(f"- {col}")
        
        print("\nPrimeiras 5 linhas de medicamentos:")
        print(medicamentos_df.head(5))
    
    if precos_df.empty:
        print("\nErro: Não foi possível extrair dados de preços do arquivo.")
    else:
        print(f"\n✅ Extraídos {len(precos_df)} registros de preços")
        print("\nColunas encontradas em preços:")
        for col in precos_df.columns:
            print(f"- {col}")
        
        print("\nPrimeiras 5 linhas de preços:")
        print(precos_df.head(5))
    
    # Salvar em CSV para inspeção
    if not medicamentos_df.empty:
        medicamentos_df.to_csv("medicamentos_teste.csv", index=False)
        print("\nArquivo medicamentos_teste.csv gerado para inspeção.")
    
    if not precos_df.empty:
        precos_df.to_csv("precos_teste.csv", index=False)
        print("Arquivo precos_teste.csv gerado para inspeção.")

if __name__ == "__main__":
    testar_processamento_arquivo()
