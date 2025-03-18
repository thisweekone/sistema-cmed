# Painel de Histórico de Preços de Medicamentos CMED

Este projeto consiste em um painel interativo para visualização e importação de dados da tabela de medicamentos da CMED (Câmara de Regulação do Mercado de Medicamentos).

## Funcionalidades

- **Importação de Dados**:
  - Upload de arquivos CSV, XLS e XLSX
  - Mapeamento inteligente de colunas
  - Interface amigável para validação de dados
  - Indicadores de carregamento para feedback visual
  - Validação e processamento seguro dos dados

- **Visualização de Dados**:
  - Listagem dos medicamentos cadastrados
  - Visualização detalhada dos preços por medicamento
  - Exportação de dados

- **Armazenamento**:
  - Integração com Supabase para armazenamento seguro dos dados
  - Estrutura otimizada para consultas rápidas

## Requisitos

- Python 3.8+
- Supabase (para armazenamento dos dados)
- Pacotes Python listados em `requirements.txt`

## Configuração

1. Clone o repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

3. Configure as credenciais do Supabase:
   - Copie o arquivo `.env.example` para `.env`
   - Preencha as credenciais do Supabase no arquivo `.env`:
     ```
     SUPABASE_URL=sua_url_do_supabase
     SUPABASE_KEY=sua_chave_do_supabase
     ```

4. Configure o banco de dados (opcional):
   ```
   python configurar_supabase.py
   ```
   
   Este script verifica e cria a tabela `medicamentos` com todos os campos necessários.

## Uso

Para iniciar a aplicação:

```
python app_flask.py
```

Acesse a interface web em http://localhost:5000

## Estrutura da Aplicação

- `app_flask.py`: Aplicação principal Flask
- `configurar_supabase.py`: Script para configuração do banco de dados
- `testar_supabase.py`: Ferramenta de diagnóstico para conexão com Supabase
- `importar_rpc.sql` e `supabase_functions.sql`: Funções SQL para Supabase

## Importação de Dados

O sistema permite importar dados da tabela CMED através de arquivos nos formatos CSV, XLS ou XLSX. O processo de importação inclui:

1. Upload do arquivo
2. Mapeamento de colunas
3. Validação dos dados
4. Confirmação e importação para o Supabase

## Solução de Problemas

Se encontrar problemas na importação ou visualização dos dados:

1. Execute o script de diagnóstico:
   ```
   python testar_supabase.py
   ```

2. Verifique as permissões (RLS) no seu projeto Supabase

3. Consulte os logs da aplicação para detalhes específicos de erros
