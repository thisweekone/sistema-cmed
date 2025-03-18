import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from supabase import create_client

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Teste de Aplicativo CMED",
    page_icon="🧪",
    layout="wide"
)

# Inicializar conexão com Supabase
@st.cache_resource
def init_connection():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

# Título principal
st.title("🧪 Teste de Aplicativo CMED")

# Verificar conexão com Supabase
try:
    supabase = init_connection()
    st.success("✅ Conexão com o Supabase estabelecida com sucesso!")
    
    # Verificar tabelas
    try:
        response = supabase.table("medicamentos").select("count", count="exact").limit(1).execute()
        st.success(f"✅ Tabela 'medicamentos' encontrada. Registros: {response.count}")
    except Exception as e:
        st.error(f"❌ Tabela 'medicamentos' não encontrada ou erro de acesso: {str(e)}")
    
    try:
        response = supabase.table("precos").select("count", count="exact").limit(1).execute()
        st.success(f"✅ Tabela 'precos' encontrada. Registros: {response.count}")
    except Exception as e:
        st.error(f"❌ Tabela 'precos' não encontrada ou erro de acesso: {str(e)}")
        
except Exception as e:
    st.error(f"❌ Erro ao conectar ao Supabase: {str(e)}")

# Exibir variáveis de ambiente (sem mostrar valores sensíveis)
st.subheader("Variáveis de Ambiente")
env_vars = {
    "SUPABASE_URL": "✓ Definido" if os.getenv("SUPABASE_URL") else "✗ Não definido",
    "SUPABASE_KEY": "✓ Definido" if os.getenv("SUPABASE_KEY") else "✗ Não definido"
}
st.json(env_vars)

# Upload de arquivo simples
st.subheader("Upload de Arquivo")
uploaded_file = st.file_uploader("Selecione um arquivo Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    st.success(f"Arquivo carregado: {uploaded_file.name}")
    
    # Tentar ler o arquivo
    try:
        df = pd.read_excel(uploaded_file)
        st.dataframe(df.head())
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")

# Rodapé
st.markdown("---")
st.markdown("Aplicativo de teste para diagnóstico")
