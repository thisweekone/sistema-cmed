import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import os
from dotenv import load_dotenv
import glob
from datetime import datetime
import importar_dados

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da página
st.set_page_config(
    page_title="Histórico de Preços CMED",
    page_icon="💊",
    layout="wide"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar conexão com Supabase
@st.cache_resource
def init_connection():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

# Função para carregar dados
@st.cache_data(ttl=3600)
def load_medicamentos():
    try:
        supabase = init_connection()
        response = supabase.table("medicamentos").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erro ao carregar medicamentos: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_precos(anos, estados, medicamentos_ids):
    try:
        supabase = init_connection()
        query = supabase.table("precos").select("*")
        
        # Filtrar por ano
        if anos:
            query = query.in_("ano", anos)
        
        # Filtrar por estado (ICMS)
        if estados:
            query = query.in_("estado", estados)
            
        # Filtrar por medicamentos
        if medicamentos_ids:
            query = query.in_("medicamento_id", medicamentos_ids)
            
        response = query.execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erro ao carregar preços: {e}")
        return pd.DataFrame()

# Função para obter anos disponíveis
@st.cache_data(ttl=3600)
def get_anos_disponiveis():
    try:
        supabase = init_connection()
        response = supabase.table("precos").select("ano").distinct().execute()
        anos = pd.DataFrame(response.data)
        if not anos.empty:
            return sorted(anos["ano"].unique())
        return []
    except Exception as e:
        st.error(f"Erro ao carregar anos disponíveis: {e}")
        return []

# Função para obter estados disponíveis
@st.cache_data(ttl=3600)
def get_estados_disponiveis():
    try:
        supabase = init_connection()
        response = supabase.table("precos").select("estado").distinct().execute()
        estados = pd.DataFrame(response.data)
        if not estados.empty:
            return sorted(estados["estado"].unique())
        return []
    except Exception as e:
        st.error(f"Erro ao carregar estados disponíveis: {e}")
        return []

# Título principal
st.title("📊 Histórico de Preços de Medicamentos - CMED")

# Criar abas
tab1, tab2 = st.tabs(["📈 Visualização", "📥 Importação de Dados"])

with tab1:
    st.markdown("Selecione medicamentos para visualizar o histórico de preços por período e estado (ICMS).")

    # Layout em colunas
    col1, col2 = st.columns([1, 3])

    # Painel de filtros
    with col1:
        st.subheader("Filtros")
        
        # Filtro de anos
        anos_disponiveis = get_anos_disponiveis()
        anos_selecionados = st.multiselect(
            "Selecione os anos",
            options=anos_disponiveis,
            default=anos_disponiveis[-2:] if len(anos_disponiveis) >= 2 else anos_disponiveis
        )
        
        # Filtro de estados (ICMS)
        estados_disponiveis = get_estados_disponiveis()
        estados_selecionados = st.multiselect(
            "Selecione os estados (ICMS)",
            options=estados_disponiveis,
            default=["SP"] if "SP" in estados_disponiveis else (estados_disponiveis[:1] if estados_disponiveis else [])
        )
        
        # Filtro de medicamentos
        medicamentos_df = load_medicamentos()
        if not medicamentos_df.empty:
            # Criar campo de busca para medicamentos
            busca_medicamento = st.text_input("Buscar medicamento", "")
            
            # Filtrar medicamentos pela busca
            if busca_medicamento:
                medicamentos_filtrados = medicamentos_df[
                    medicamentos_df['produto'].str.contains(busca_medicamento, case=False) |
                    medicamentos_df['apresentacao'].str.contains(busca_medicamento, case=False) |
                    medicamentos_df['laboratorio'].str.contains(busca_medicamento, case=False)
                ]
            else:
                medicamentos_filtrados = medicamentos_df
                
            # Criar rótulo para exibição
            medicamentos_filtrados['rotulo'] = medicamentos_filtrados.apply(
                lambda x: f"{x['produto']} - {x['apresentacao']} ({x['laboratorio']})", 
                axis=1
            )
            
            # Ordenar por nome do produto
            opcoes_medicamentos = medicamentos_filtrados.set_index("id").sort_values("produto")["rotulo"].to_dict()
            
            medicamentos_selecionados = st.multiselect(
                "Selecione os medicamentos",
                options=list(opcoes_medicamentos.keys()),
                format_func=lambda x: opcoes_medicamentos[x]
            )
        else:
            st.warning("Nenhum medicamento encontrado no banco de dados.")
            medicamentos_selecionados = []
        
        # Botão para aplicar filtros
        if st.button("Aplicar Filtros", type="primary"):
            st.session_state.filtros_aplicados = True
        else:
            if 'filtros_aplicados' not in st.session_state:
                st.session_state.filtros_aplicados = False

    # Área de visualização
    with col2:
        if st.session_state.filtros_aplicados and medicamentos_selecionados and anos_selecionados and estados_selecionados:
            # Carregar dados de preços
            precos_df = load_precos(anos_selecionados, estados_selecionados, medicamentos_selecionados)
            
            if not precos_df.empty:
                # Mesclar com informações dos medicamentos
                if not medicamentos_df.empty:
                    precos_df = precos_df.merge(
                        medicamentos_df[["id", "produto", "apresentacao", "laboratorio"]],
                        left_on="medicamento_id",
                        right_on="id",
                        how="left"
                    )
                    
                    # Criar rótulo completo para o medicamento
                    precos_df["medicamento"] = precos_df.apply(
                        lambda x: f"{x['produto']} - {x['apresentacao']} ({x['laboratorio']})", 
                        axis=1
                    )
                    
                    # Verificar quais colunas de preço estão disponíveis
                    colunas_preco = []
                    if 'pf_sem_impostos' in precos_df.columns and precos_df['pf_sem_impostos'].notna().any():
                        colunas_preco.append(('pf_sem_impostos', 'Preço Fábrica (sem impostos)'))
                    if 'pf_com_impostos' in precos_df.columns and precos_df['pf_com_impostos'].notna().any():
                        colunas_preco.append(('pf_com_impostos', 'Preço Fábrica (com impostos)'))
                    if 'pmc_sem_impostos' in precos_df.columns and precos_df['pmc_sem_impostos'].notna().any():
                        colunas_preco.append(('pmc_sem_impostos', 'Preço Máximo ao Consumidor (sem impostos)'))
                    if 'pmc_com_impostos' in precos_df.columns and precos_df['pmc_com_impostos'].notna().any():
                        colunas_preco.append(('pmc_com_impostos', 'Preço Máximo ao Consumidor (com impostos)'))
                    
                    if not colunas_preco:
                        st.warning("Não foram encontrados dados de preço para os filtros selecionados.")
                    else:
                        coluna_preco, nome_coluna = colunas_preco[0]  # Usar a primeira coluna disponível por padrão
                        
                        # Permitir ao usuário escolher qual preço visualizar
                        if len(colunas_preco) > 1:
                            opcoes_tipo_preco = {col: nome for col, nome in colunas_preco}
                            tipo_preco_selecionado = st.radio(
                                "Tipo de preço a visualizar:",
                                options=list(opcoes_tipo_preco.keys()),
                                format_func=lambda x: opcoes_tipo_preco[x],
                                horizontal=True
                            )
                            coluna_preco = tipo_preco_selecionado
                            nome_coluna = opcoes_tipo_preco[tipo_preco_selecionado]
                        
                        # Preparar dados para visualização
                        df_plot = precos_df.copy()
                        
                        # Adicionar informação do mês (se disponível)
                        if 'mes' in df_plot.columns and df_plot['mes'].notna().any():
                            df_plot['data'] = df_plot.apply(lambda x: f"{x['ano']}-{x['mes']:02d}" if pd.notna(x['mes']) else f"{x['ano']}", axis=1)
                        else:
                            df_plot['data'] = df_plot['ano'].astype(str)
                        
                        # Gráfico de linhas
                        st.subheader(f"Evolução de {nome_coluna} por Ano/Mês")
                        
                        fig = px.line(
                            df_plot, 
                            x="data", 
                            y=coluna_preco,
                            color="medicamento",
                            markers=True,
                            title=f"Evolução de {nome_coluna} por Ano/Mês",
                            labels={
                                "data": "Período",
                                coluna_preco: nome_coluna,
                                "medicamento": "Medicamento"
                            }
                        )
                        
                        # Ajustar layout
                        fig.update_layout(
                            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                            margin=dict(l=20, r=20, t=50, b=20),
                            height=500
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Tabela de dados
                        st.subheader("Dados Detalhados")
                        
                        # Colunas para exibir na tabela
                        colunas_tabela = ["medicamento", "ano"]
                        if 'mes' in df_plot.columns and df_plot['mes'].notna().any():
                            colunas_tabela.append("mes")
                        colunas_tabela.append("estado")
                        
                        # Adicionar colunas de preço
                        for col, nome in colunas_preco:
                            colunas_tabela.append(col)
                        
                        # Adicionar colunas de flags
                        for flag in ['restricao_hospitalar', 'cap', 'confaz87', 'icms_0']:
                            if flag in df_plot.columns and df_plot[flag].any():
                                colunas_tabela.append(flag)
                        
                        # Renomear colunas para melhor visualização
                        colunas_rename = {
                            "medicamento": "Medicamento",
                            "ano": "Ano",
                            "mes": "Mês",
                            "estado": "Estado (ICMS)",
                            "pf_sem_impostos": "PF sem impostos",
                            "pf_com_impostos": "PF com impostos",
                            "pmc_sem_impostos": "PMC sem impostos",
                            "pmc_com_impostos": "PMC com impostos",
                            "restricao_hospitalar": "Restrição Hospitalar",
                            "cap": "CAP",
                            "confaz87": "CONFAZ 87",
                            "icms_0": "ICMS 0%"
                        }
                        
                        # Criar tabela
                        tabela_df = df_plot[colunas_tabela].rename(columns=colunas_rename)
                        
                        # Ordenar por medicamento, ano, mês e estado
                        ordem_colunas = ["Medicamento", "Ano"]
                        if "Mês" in tabela_df.columns:
                            ordem_colunas.append("Mês")
                        ordem_colunas.append("Estado (ICMS)")
                        
                        tabela_df = tabela_df.sort_values(by=ordem_colunas)
                        
                        # Exibir tabela
                        st.dataframe(tabela_df, use_container_width=True)
                else:
                    st.warning("Não foi possível obter informações detalhadas dos medicamentos.")
            else:
                st.info("Nenhum dado encontrado para os filtros selecionados.")
        elif st.session_state.filtros_aplicados:
            st.info("Selecione pelo menos um medicamento, um ano e um estado para visualizar os dados.")
        else:
            st.info("Use os filtros ao lado para selecionar medicamentos, anos e estados, e clique em 'Aplicar Filtros' para visualizar os dados.")

with tab2:
    st.markdown("## 📥 Importação de Dados CMED")
    st.markdown("Use esta página para importar dados da CMED para o banco de dados Supabase.")

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
            st.info("Você precisa criar esta tabela manualmente no painel do Supabase.")
        
        try:
            response = supabase.table("precos").select("count", count="exact").limit(1).execute()
            st.success(f"✅ Tabela 'precos' encontrada. Registros: {response.count}")
        except Exception as e:
            st.error(f"❌ Tabela 'precos' não encontrada ou erro de acesso: {str(e)}")
            st.info("Você precisa criar esta tabela manualmente no painel do Supabase.")
            
    except Exception as e:
        st.error(f"❌ Erro ao conectar ao Supabase: {str(e)}")
        st.info("Verifique suas credenciais no arquivo .env")
        st.stop()

    # Layout em colunas
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Importação Manual")
        
        # Upload de arquivo
        uploaded_file = st.file_uploader("Selecione um arquivo Excel da CMED", type=["xlsx", "xls"])
        
        if uploaded_file is not None:
            # Salvar arquivo temporariamente
            temp_file = os.path.join(os.getcwd(), "temp_cmed_file.xlsx")
            with open(temp_file, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.success(f"Arquivo carregado: {uploaded_file.name}")
            
            # Extrair ano e mês do nome do arquivo
            nome_arquivo = uploaded_file.name
            ano, mes = importar_dados.extrair_data_do_arquivo(nome_arquivo)
            
            # Formulário para ano e mês
            with st.form("dados_form"):
                if ano:
                    ano_input = st.number_input("Ano", min_value=2000, max_value=2100, value=ano)
                else:
                    ano_input = st.number_input("Ano", min_value=2000, max_value=2100, value=datetime.now().year)
                
                if mes:
                    mes_input = st.number_input("Mês (opcional)", min_value=1, max_value=12, value=mes)
                else:
                    mes_input = st.number_input("Mês (opcional)", min_value=1, max_value=12, value=1)
                
                submit_button = st.form_submit_button("Processar e Importar")
                
                if submit_button:
                    with st.spinner("Processando arquivo..."):
                        try:
                            # Processar arquivo
                            medicamentos_df, precos_df = importar_dados.processar_arquivo_cmed(temp_file, ano_input, mes_input)
                            
                            if medicamentos_df.empty or precos_df.empty:
                                st.error("Não foi possível extrair dados do arquivo.")
                            else:
                                st.success(f"Extraídos {len(medicamentos_df)} medicamentos e {len(precos_df)} registros de preços.")
                                
                                # Mostrar prévia dos dados
                                with st.expander("Prévia dos Medicamentos"):
                                    st.dataframe(medicamentos_df.head(10))
                                
                                with st.expander("Prévia dos Preços"):
                                    st.dataframe(precos_df.head(10))
                                
                                # Importar para Supabase
                                if st.button("Confirmar Importação para Supabase"):
                                    with st.spinner("Importando dados para o Supabase..."):
                                        try:
                                            importar_dados.importar_para_supabase(medicamentos_df, precos_df)
                                            st.success("✅ Dados importados com sucesso!")
                                            # Limpar cache para atualizar os dados
                                            st.cache_data.clear()
                                        except Exception as e:
                                            st.error(f"Erro ao importar dados: {str(e)}")
                        except Exception as e:
                            st.error(f"Erro ao processar arquivo: {str(e)}")
                    
                    # Remover arquivo temporário
                    try:
                        os.remove(temp_file)
                    except:
                        pass

    with col2:
        st.subheader("Importação por Diretório")
        
        # Caminho do diretório
        dir_path = st.text_input("Digite o caminho para o diretório com os arquivos CMED:")
        
        if dir_path and os.path.isdir(dir_path):
            # Listar arquivos Excel
            excel_files = glob.glob(os.path.join(dir_path, "*.xlsx")) + glob.glob(os.path.join(dir_path, "*.xls"))
            
            if not excel_files:
                st.warning("Nenhum arquivo Excel encontrado no diretório especificado.")
            else:
                st.success(f"Encontrados {len(excel_files)} arquivos Excel.")
                
                # Mostrar lista de arquivos
                files_df = pd.DataFrame({
                    "Arquivo": [os.path.basename(f) for f in excel_files],
                    "Tamanho (KB)": [round(os.path.getsize(f) / 1024, 2) for f in excel_files],
                    "Data de Modificação": [datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S") for f in excel_files]
                })
                
                st.dataframe(files_df)
                
                # Opção para importar todos
                if st.button("Importar Todos os Arquivos"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, file in enumerate(excel_files):
                        file_name = os.path.basename(file)
                        status_text.text(f"Processando {file_name}... ({i+1}/{len(excel_files)})")
                        
                        # Extrair ano e mês do nome do arquivo
                        ano, mes = importar_dados.extrair_data_do_arquivo(file_name)
                        
                        if not ano:
                            status_text.text(f"Pulando {file_name} - Não foi possível determinar o ano.")
                            continue
                        
                        try:
                            # Processar arquivo
                            medicamentos_df, precos_df = importar_dados.processar_arquivo_cmed(file, ano, mes)
                            
                            if not medicamentos_df.empty and not precos_df.empty:
                                # Importar para Supabase
                                importar_dados.importar_para_supabase(medicamentos_df, precos_df)
                                status_text.text(f"✅ Importado {file_name} - {len(medicamentos_df)} medicamentos, {len(precos_df)} preços")
                            else:
                                status_text.text(f"❌ Falha ao processar {file_name} - Dados não extraídos")
                        except Exception as e:
                            status_text.text(f"❌ Erro ao processar {file_name}: {str(e)}")
                        
                        # Atualizar barra de progresso
                        progress_bar.progress((i + 1) / len(excel_files))
                    
                    status_text.text("Importação concluída!")
                    st.success("Processo de importação finalizado. Verifique as mensagens acima para detalhes.")
                    # Limpar cache para atualizar os dados
                    st.cache_data.clear()

# Rodapé
st.markdown("---")
st.markdown("Dados obtidos da tabela CMED (Câmara de Regulação do Mercado de Medicamentos)")
