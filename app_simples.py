import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import sys

# Configuração da página
st.set_page_config(
    page_title="Histórico de Preços de Medicamentos - CMED",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Histórico de Preços de Medicamentos - CMED")

# Criar abas
tab1, tab2 = st.tabs(["📈 Visualização", "📥 Importação de Dados"])

with tab1:
    st.header("Visualização de Dados")
    st.write("Esta aba permitirá visualizar o histórico de preços dos medicamentos.")
    
    # Placeholder para futura implementação
    st.info("Funcionalidade de visualização em desenvolvimento.")

with tab2:
    st.header("Importação de Dados")
    st.write("Esta aba permite importar arquivos da CMED para o banco de dados.")
    
    # Verificar ambiente Python
    st.subheader("Informações do Ambiente")
    st.write(f"Python versão: {sys.version}")
    st.write(f"Streamlit versão: {st.__version__}")
    
    # Verificar variáveis de ambiente
    st.subheader("Variáveis de Ambiente")
    load_dotenv()
    env_vars = {
        "SUPABASE_URL": "✓ Definido" if os.getenv("SUPABASE_URL") else "✗ Não definido",
        "SUPABASE_KEY": "✓ Definido" if os.getenv("SUPABASE_KEY") else "✗ Não definido"
    }
    st.json(env_vars)
    
    # Upload de arquivo
    st.subheader("Upload de Arquivo")
    uploaded_file = st.file_uploader("Selecione um arquivo Excel da CMED", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        st.success(f"Arquivo carregado: {uploaded_file.name}")
        
        # Tentar ler o arquivo
        try:
            df = pd.read_excel(uploaded_file)
            st.write(f"O arquivo contém {len(df)} linhas e {len(df.columns)} colunas.")
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

# Rodapé
st.markdown("---")
st.markdown("Dados obtidos da tabela CMED (Câmara de Regulação do Mercado de Medicamentos)")
