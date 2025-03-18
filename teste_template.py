from flask import Flask, render_template_string
import pandas as pd

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
        
        <form method="post" action="/confirmar_importacao/{{ session_id }}">
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
                <a href="/mapear_colunas/{{ session_id }}" class="btn btn-secondary">Voltar</a>
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

@app.route('/')
def teste_template():
    # Criar dados de teste
    df_teste = pd.DataFrame({
        'Substância': ['Substância 1', 'Substância 2'],
        'Laboratório': ['Lab 1', 'Lab 2'],
        'Código GGREM': ['123', '456'],
        'PF': [10.5, 20.3]
    })
    
    mapeamento_teste = {
        'substancia': 'Substância',
        'laboratorio': 'Laboratório',
        'codigo_ggrem': 'Código GGREM',
        'pf': 'PF'
    }
    
    # Renderizar o template de confirmação com dados de teste
    return render_template_string(TEMPLATE_CONFIRMACAO, 
                                 session_id='teste123',
                                 arquivo_original='arquivo_teste.xlsx',
                                 mapeamento=mapeamento_teste,
                                 df_preview=df_teste,
                                 campos_necessarios=CAMPOS_NECESSARIOS,
                                 message=None,
                                 message_type=None)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
