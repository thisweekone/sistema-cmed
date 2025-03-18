import os
import pandas as pd
import pickle
from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Campos necessários para o mapeamento
CAMPOS_NECESSARIOS = [
    {'id': 'substancia', 'nome': 'Substância', 'obrigatorio': True},
    {'id': 'laboratorio', 'nome': 'Laboratório', 'obrigatorio': True},
    {'id': 'codigo_ggrem', 'nome': 'Código GGREM', 'obrigatorio': True},
    {'id': 'pf', 'nome': 'PF', 'obrigatorio': True},
    {'id': 'pmvg', 'nome': 'PMVG', 'obrigatorio': False},
]

# Template HTML para a página de confirmação de importação
TEMPLATE_CONFIRMACAO = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Confirmar Importação - CMED</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding-top: 20px;
            padding-bottom: 20px;
        }
        .header {
            border-bottom: 1px solid #e5e5e5;
            margin-bottom: 30px;
            padding-bottom: 10px;
        }
        .preview-table {
            font-size: 0.9em;
        }
        .table-responsive {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Confirmar Importação</h1>
            <p class="lead">Arquivo: {{ arquivo_original }}</p>
        </div>
        
        {% if message %}
        <div class="alert alert-{{ 'success' if message_type == 'success' else 'danger' }}">
            {{ message }}
        </div>
        {% endif %}
        
        <form method="post" action="/confirmar/{{ session_id }}">
            <div class="row">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h3>Mapeamento de Colunas</h3>
                        </div>
                        <div class="card-body">
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>Campo do Sistema</th>
                                        <th>Coluna do Arquivo</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {% for campo_id, coluna in mapeamento.items() %}
                                    <tr>
                                        <td>
                                            {% for campo in campos_necessarios %}
                                                {% if campo.id == campo_id %}
                                                    {{ campo.nome }}
                                                    {% if campo.obrigatorio %}
                                                    <span class="text-danger">*</span>
                                                    {% endif %}
                                                {% endif %}
                                            {% endfor %}
                                        </td>
                                        <td>{{ coluna }}</td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h3>Prévia dos Dados</h3>
                        </div>
                        <div class="card-body">
                            <div class="table-responsive">
                                <table class="table table-striped table-sm preview-table">
                                    <thead>
                                        <tr>
                                            {% for col in df_preview.columns %}
                                            <th>{{ col }}</th>
                                            {% endfor %}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {% for index, row in df_preview.iterrows() %}
                                        <tr>
                                            {% for col in df_preview.columns %}
                                            <td>{{ row[col] }}</td>
                                            {% endfor %}
                                        </tr>
                                        {% endfor %}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="row mt-4">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-header">
                            <h3>Informações da Publicação</h3>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <label for="data_publicacao" class="form-label">Data de Publicação</label>
                                <input type="date" class="form-control" id="data_publicacao" name="data_publicacao" required>
                                <div class="form-text">Informe a data de publicação dos valores da tabela CMED que está sendo importada.</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="d-flex justify-content-between mt-4">
                <a href="/mapear/{{ session_id }}" class="btn btn-secondary">Voltar</a>
                <button type="submit" class="btn btn-success">Confirmar e Importar</button>
            </div>
        </form>
        
        <footer class="mt-5 pt-3 text-muted border-top">
            <p>Dados obtidos da tabela CMED (Câmara de Regulação do Mercado de Medicamentos)</p>
        </footer>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Template para a página de mapeamento
TEMPLATE_MAPEAMENTO = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mapear Colunas - CMED</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding-top: 20px;
            padding-bottom: 20px;
        }
        .header {
            border-bottom: 1px solid #e5e5e5;
            margin-bottom: 30px;
            padding-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Mapear Colunas</h1>
            <p class="lead">Arquivo: {{ arquivo_original }}</p>
        </div>
        
        {% if message %}
        <div class="alert alert-{{ 'success' if message_type == 'success' else 'danger' }}">
            {{ message }}
        </div>
        {% endif %}
        
        <form method="post" action="/mapear/{{ session_id }}">
            <div class="card">
                <div class="card-header">
                    <h3>Mapeamento de Colunas</h3>
                </div>
                <div class="card-body">
                    <p>Selecione as colunas do arquivo que correspondem aos campos do sistema:</p>
                    
                    <div class="row">
                        {% for campo in campos_necessarios %}
                        <div class="col-md-6 mb-3">
                            <label for="campo_{{ campo.id }}" class="form-label">
                                {{ campo.nome }}
                                {% if campo.obrigatorio %}
                                <span class="text-danger">*</span>
                                {% endif %}
                            </label>
                            <select class="form-select" id="campo_{{ campo.id }}" name="campo_{{ campo.id }}" {% if campo.obrigatorio %}required{% endif %}>
                                <option value="">Selecione uma coluna</option>
                                {% for coluna in colunas %}
                                <option value="{{ coluna }}">{{ coluna }}</option>
                                {% endfor %}
                            </select>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-header">
                    <h3>Prévia dos Dados</h3>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    {% for col in df_preview.columns %}
                                    <th>{{ col }}</th>
                                    {% endfor %}
                                </tr>
                            </thead>
                            <tbody>
                                {% for index, row in df_preview.iterrows() %}
                                <tr>
                                    {% for col in df_preview.columns %}
                                    <td>{{ row[col] }}</td>
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <div class="d-flex justify-content-between mt-4">
                <a href="/" class="btn btn-secondary">Cancelar</a>
                <button type="submit" class="btn btn-primary">Avançar</button>
            </div>
        </form>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Template para a página inicial
TEMPLATE_INICIAL = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Teste de Importação - CMED</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding-top: 20px;
            padding-bottom: 20px;
        }
        .header {
            border-bottom: 1px solid #e5e5e5;
            margin-bottom: 30px;
            padding-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Teste de Importação</h1>
            <p class="lead">Selecione um arquivo para importar</p>
        </div>
        
        {% if message %}
        <div class="alert alert-{{ 'success' if message_type == 'success' else 'danger' }}">
            {{ message }}
        </div>
        {% endif %}
        
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header">
                        <h3>Importar Arquivo</h3>
                    </div>
                    <div class="card-body">
                        <form method="post" action="/" enctype="multipart/form-data">
                            <div class="mb-3">
                                <label for="file" class="form-label">Selecione um arquivo</label>
                                <input type="file" class="form-control" id="file" name="file" required>
                                <div class="form-text">Formatos suportados: Excel (.xlsx, .xls) e CSV (.csv)</div>
                            </div>
                            <button type="submit" class="btn btn-primary">Enviar</button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Função para gerar um ID de sessão único
def gerar_session_id():
    import uuid
    return str(uuid.uuid4())

# Funções para salvar e carregar dados temporários
def salvar_dados_temp(session_id, dados):
    os.makedirs('temp_data', exist_ok=True)
    with open(f'temp_data/{session_id}.pkl', 'wb') as f:
        pickle.dump(dados, f)

def carregar_dados_temp(session_id):
    try:
        with open(f'temp_data/{session_id}.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Verificar se o arquivo foi enviado
        if 'file' not in request.files:
            return render_template_string(TEMPLATE_INICIAL, 
                                         message='Nenhum arquivo enviado',
                                         message_type='error')
        
        file = request.files['file']
        
        if file.filename == '':
            return render_template_string(TEMPLATE_INICIAL, 
                                         message='Nome de arquivo vazio',
                                         message_type='error')
        
        # Verificar extensão do arquivo
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.csv')):
            return render_template_string(TEMPLATE_INICIAL, 
                                         message='Formato de arquivo não suportado. Use arquivos Excel (.xlsx, .xls) ou CSV (.csv)',
                                         message_type='error')
        
        # Criar diretório temporário se não existir
        os.makedirs('temp_uploads', exist_ok=True)
        os.makedirs('temp_data', exist_ok=True)
        
        # Gerar um ID de sessão único
        session_id = gerar_session_id()
        
        # Salvar o arquivo temporariamente
        filename = file.filename
        temp_path = os.path.join('temp_uploads', f"{session_id}_{filename}")
        file.save(temp_path)
        
        # Processar o arquivo
        try:
            if file.filename.lower().endswith(('.xlsx', '.xls')):
                # Processar arquivo Excel
                df = pd.read_excel(temp_path)
            elif file.filename.lower().endswith('.csv'):
                # Processar arquivo CSV
                try:
                    # Tentar diferentes encodings e delimitadores
                    encodings = ['utf-8', 'latin1', 'iso-8859-1']
                    delimiters = [',', ';', '\t']
                    
                    df = None
                    for encoding in encodings:
                        for delimiter in delimiters:
                            try:
                                df = pd.read_csv(temp_path, encoding=encoding, sep=delimiter)
                                # Se conseguiu ler e tem mais de uma coluna, provavelmente está correto
                                if len(df.columns) > 1:
                                    print(f"CSV lido com sucesso usando encoding={encoding} e delimiter={delimiter}")
                                    break
                            except Exception as e:
                                print(f"Erro ao ler CSV com encoding={encoding} e delimiter={delimiter}: {str(e)}")
                                continue
                        if df is not None and len(df.columns) > 1:
                            break
                    
                    if df is None or len(df.columns) <= 1:
                        raise ValueError("Não foi possível ler o arquivo CSV corretamente. Verifique o formato do arquivo.")
                except Exception as e:
                    raise ValueError(f"Erro ao processar o arquivo CSV: {str(e)}")
            
            # Salvar dados temporários
            dados_temp = {
                'df': df,
                'arquivo_original': filename,
                'temp_path': temp_path
            }
            
            salvar_dados_temp(session_id, dados_temp)
            
            # Redirecionar para a página de mapeamento
            return redirect(url_for('mapear', session_id=session_id))
            
        except Exception as e:
            # Limpar arquivos temporários se existirem
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            
            return render_template_string(TEMPLATE_INICIAL, 
                                         message=f'Erro ao processar o arquivo: {str(e)}',
                                         message_type='error')
    
    # Método GET - exibir o formulário de upload
    return render_template_string(TEMPLATE_INICIAL, 
                                 message=None,
                                 message_type=None)

@app.route('/mapear/<session_id>', methods=['GET', 'POST'])
def mapear(session_id):
    # Carregar dados temporários
    dados_temp = carregar_dados_temp(session_id)
    
    if not dados_temp:
        return render_template_string(TEMPLATE_INICIAL, 
                                     message='Sessão expirada ou inválida. Por favor, faça o upload novamente.',
                                     message_type='error')
    
    df = dados_temp['df']
    arquivo_original = dados_temp['arquivo_original']
    
    if request.method == 'POST':
        # Processar o mapeamento de colunas
        mapeamento = {}
        for campo in CAMPOS_NECESSARIOS:
            campo_id = campo['id']
            coluna = request.form.get(f'campo_{campo_id}')
            
            # Verificar se os campos obrigatórios foram mapeados
            if campo['obrigatorio'] and not coluna:
                return render_template_string(TEMPLATE_MAPEAMENTO, 
                                             session_id=session_id,
                                             arquivo_original=arquivo_original,
                                             colunas=df.columns.tolist(),
                                             df_preview=df.head(5),
                                             campos_necessarios=CAMPOS_NECESSARIOS,
                                             message=f'O campo {campo["nome"]} é obrigatório.',
                                             message_type='error')
            
            if coluna:
                mapeamento[campo_id] = coluna
        
        # Atualizar dados temporários com o mapeamento
        dados_temp['mapeamento'] = mapeamento
        salvar_dados_temp(session_id, dados_temp)
        
        # Redirecionar para a página de confirmação
        return redirect(url_for('confirmar', session_id=session_id))
    
    # Método GET - exibir o formulário de mapeamento
    return render_template_string(TEMPLATE_MAPEAMENTO, 
                                 session_id=session_id,
                                 arquivo_original=arquivo_original,
                                 colunas=df.columns.tolist(),
                                 df_preview=df.head(5),
                                 campos_necessarios=CAMPOS_NECESSARIOS,
                                 message=None,
                                 message_type=None)

@app.route('/confirmar/<session_id>', methods=['GET', 'POST'])
def confirmar(session_id):
    # Carregar dados temporários
    dados_temp = carregar_dados_temp(session_id)
    
    # Log para depuração
    print("="*50)
    print(f"Rota de confirmação acessada: {session_id}")
    print(f"Método: {request.method}")
    if request.method == 'POST':
        print(f"Dados do formulário: {request.form}")
        print(f"Data de publicação: {request.form.get('data_publicacao')}")
    print("="*50)
    
    if not dados_temp or 'mapeamento' not in dados_temp:
        return render_template_string(TEMPLATE_INICIAL, 
                                     message='Sessão expirada ou inválida. Por favor, faça o upload novamente.',
                                     message_type='error')
    
    df = dados_temp['df']
    mapeamento = dados_temp['mapeamento']
    arquivo_original = dados_temp['arquivo_original']
    
    if request.method == 'POST':
        # Processar a importação final
        try:
            # Verificar se a data de publicação foi fornecida
            data_publicacao = request.form.get('data_publicacao')
            if not data_publicacao:
                return render_template_string(TEMPLATE_CONFIRMACAO, 
                                             session_id=session_id,
                                             arquivo_original=arquivo_original,
                                             mapeamento=mapeamento,
                                             df_preview=df.head(5),
                                             campos_necessarios=CAMPOS_NECESSARIOS,
                                             message='A data de publicação é obrigatória.',
                                             message_type='error')
            
            # Criar um novo DataFrame com as colunas mapeadas
            df_mapeado = pd.DataFrame()
            for campo_id, coluna_original in mapeamento.items():
                df_mapeado[campo_id] = df[coluna_original]
            
            # Simulação de salvamento
            registros_importados = len(df_mapeado)
            
            # Limpar os dados temporários
            try:
                os.remove(f'temp_data/{session_id}.pkl')
                # Remover o arquivo temporário se existir
                temp_path = dados_temp.get('temp_path')
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                print(f"Aviso: Não foi possível remover arquivos temporários: {str(e)}")
            
            return render_template_string(TEMPLATE_INICIAL, 
                                         message=f'Arquivo {arquivo_original} importado com sucesso! Foram processados {registros_importados} registros com data de publicação {data_publicacao}.',
                                         message_type='success')
        except Exception as e:
            import traceback
            print(f"Erro ao processar importação final: {str(e)}")
            print(traceback.format_exc())
            
            return render_template_string(TEMPLATE_CONFIRMACAO, 
                                         session_id=session_id,
                                         arquivo_original=arquivo_original,
                                         mapeamento=mapeamento,
                                         df_preview=df.head(5),
                                         campos_necessarios=CAMPOS_NECESSARIOS,
                                         message=f'Erro ao processar a importação: {str(e)}',
                                         message_type='error')
    
    # Renderizar o template de confirmação
    print("="*50)
    print("Renderizando template de confirmação")
    print("="*50)
    return render_template_string(TEMPLATE_CONFIRMACAO, 
                                 session_id=session_id,
                                 arquivo_original=arquivo_original,
                                 mapeamento=mapeamento,
                                 df_preview=df.head(5),
                                 campos_necessarios=CAMPOS_NECESSARIOS,
                                 message=None,
                                 message_type=None)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
