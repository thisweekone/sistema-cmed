# Resumo do Projeto CMED - Histórico de Preços de Medicamentos

## Objetivo
Criar uma aplicação web para visualizar o histórico de preços de medicamentos da CMED (Câmara de Regulação do Mercado de Medicamentos), permitindo análises comparativas por período e por estado (ICMS).

## Componentes do Sistema

### 1. Banco de Dados (Supabase)
- **Tabela `medicamentos`**: Armazena informações sobre os medicamentos
  - Colunas: id, substancia, produto, apresentacao, laboratorio, classe_terapeutica, tipo_produto, regime_preco, tarja, lista_concessao
- **Tabela `precos`**: Armazena o histórico de preços por medicamento, ano, mês e estado
  - Colunas: id, medicamento_id, ano, mes, estado, pf_sem_impostos, pf_com_impostos, pmc_sem_impostos, pmc_com_impostos, restricao_hospitalar, cap, confaz87, icms_0

### 2. Scripts de Processamento
- **`importar_dados.py`**: Processa arquivos Excel da CMED e importa para o Supabase
- **`setup_database.py`**: Fornece instruções para configurar o banco de dados
- **`verificar_conexao.py`**: Verifica a conexão com o Supabase e o status das tabelas
- **`testar_importacao.py`**: Testa o processamento de arquivos CMED sem importar para o banco

### 3. Interface Web (Streamlit)
- **`app.py`**: Aplicação Streamlit que permite:
  - Buscar e selecionar medicamentos
  - Filtrar por período (anos)
  - Filtrar por estado (ICMS)
  - Visualizar dados em gráficos de linha, barras e tabelas
  - Exportar dados para CSV

## Fluxo de Uso

1. **Configuração Inicial**:
   - Configurar credenciais do Supabase no arquivo `.env`
   - Criar tabelas no Supabase (manualmente ou usando o SQL fornecido)

2. **Importação de Dados**:
   - Baixar arquivos Excel da CMED
   - Executar `importar_dados.py` para processar e importar os dados

3. **Visualização**:
   - Executar `streamlit run app.py` para iniciar a aplicação web
   - Selecionar medicamentos, períodos e estados para análise
   - Visualizar gráficos e tabelas comparativas

## Arquivos Auxiliares

- **`criar_tabelas.sql`**: SQL para criar as tabelas no Supabase
- **`requirements.txt`**: Lista de dependências Python
- **`.env`**: Arquivo de configuração com credenciais (não versionado)
- **`.env.example`**: Exemplo de arquivo de configuração

## Próximos Passos

1. Criar as tabelas no Supabase
2. Importar dados da CMED
3. Testar a visualização na aplicação Streamlit
4. Implementar melhorias na interface e funcionalidades adicionais

## Notas Importantes

- Os arquivos da CMED podem variar em formato ao longo dos anos
- O script de importação tenta lidar com essas variações automaticamente
- É necessário ter uma conta no Supabase para armazenar os dados
