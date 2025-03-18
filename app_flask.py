from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import pandas as pd
import os
import json
import re
import gdown
import tempfile
from dotenv import load_dotenv
import webbrowser
import threading
import time
import pickle
import uuid
import magic
from werkzeug.utils import secure_filename
from supabase import create_client
import numpy as np
import datetime
import math
import requests

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__)

# Definir os campos necessários para o sistema
CAMPOS_NECESSARIOS = [
    {"id": "substancia", "nome": "Substância", "descricao": "Nome da substância ativa do medicamento", "obrigatorio": True},
    {"id": "cnpj", "nome": "CNPJ", "descricao": "CNPJ do laboratório", "obrigatorio": True},
    {"id": "laboratorio", "nome": "Laboratório", "descricao": "Nome do laboratório", "obrigatorio": True},
    {"id": "codigo_ggrem", "nome": "Código GGREM", "descricao": "Código de identificação do medicamento na ANVISA", "obrigatorio": False},
    {"id": "registro", "nome": "Registro", "descricao": "Número de registro do medicamento", "obrigatorio": True},
    {"id": "ean_1", "nome": "EAN 1", "descricao": "Código de barras do medicamento (1)", "obrigatorio": False},
    {"id": "ean_2", "nome": "EAN 2", "descricao": "Código de barras do medicamento (2)", "obrigatorio": False},
    {"id": "ean_3", "nome": "EAN 3", "descricao": "Código de barras do medicamento (3)", "obrigatorio": False},
    {"id": "produto", "nome": "Produto", "descricao": "Nome comercial do produto", "obrigatorio": True},
    {"id": "apresentacao", "nome": "Apresentação", "descricao": "Forma de apresentação do medicamento", "obrigatorio": True},
    {"id": "classe_terapeutica", "nome": "Classe Terapêutica", "descricao": "Classificação terapêutica do medicamento", "obrigatorio": False},
    {"id": "tipo_produto", "nome": "Tipo de Produto", "descricao": "Classificação do tipo de produto", "obrigatorio": False},
    {"id": "regime_preco", "nome": "Regime de Preço", "descricao": "Regime de controle de preços", "obrigatorio": False},
    {"id": "pf_sem_impostos", "nome": "PF Sem Impostos", "descricao": "Preço de fábrica sem impostos", "obrigatorio": False},
    {"id": "pf_0", "nome": "PF 0%", "descricao": "Preço de fábrica 0%", "obrigatorio": False},
    {"id": "pf_12", "nome": "PF 12%", "descricao": "Preço de fábrica 12%", "obrigatorio": False},
    {"id": "pf_12_alc", "nome": "PF 12% ALC", "descricao": "Preço de fábrica 12% ALC", "obrigatorio": False},
    {"id": "pf_17", "nome": "PF 17%", "descricao": "Preço de fábrica 17%", "obrigatorio": False},
    {"id": "pf_17_alc", "nome": "PF 17% ALC", "descricao": "Preço de fábrica 17% ALC", "obrigatorio": False},
    {"id": "pf_17_5", "nome": "PF 17,5%", "descricao": "Preço de fábrica 17,5%", "obrigatorio": False},
    {"id": "pf_17_5_alc", "nome": "PF 17,5% ALC", "descricao": "Preço de fábrica 17,5% ALC", "obrigatorio": False},
    {"id": "pf_18", "nome": "PF 18%", "descricao": "Preço de fábrica 18%", "obrigatorio": False},
    {"id": "pf_18_alc", "nome": "PF 18% ALC", "descricao": "Preço de fábrica 18% ALC", "obrigatorio": False},
    {"id": "pf_19", "nome": "PF 19%", "descricao": "Preço de fábrica 19%", "obrigatorio": False},
    {"id": "pf_19_alc", "nome": "PF 19% ALC", "descricao": "Preço de fábrica 19% ALC", "obrigatorio": False},
    {"id": "pf_19_5", "nome": "PF 19,5%", "descricao": "Preço de fábrica 19,5%", "obrigatorio": False},
    {"id": "pf_19_5_alc", "nome": "PF 19,5% ALC", "descricao": "Preço de fábrica 19,5% ALC", "obrigatorio": False},
    {"id": "pf_20", "nome": "PF 20%", "descricao": "Preço de fábrica 20%", "obrigatorio": False},
    {"id": "pf_20_alc", "nome": "PF 20% ALC", "descricao": "Preço de fábrica 20% ALC", "obrigatorio": False},
    {"id": "pf_20_5", "nome": "PF 20,5%", "descricao": "Preço de fábrica 20,5%", "obrigatorio": False},
    {"id": "pf_21", "nome": "PF 21%", "descricao": "Preço de fábrica 21%", "obrigatorio": False},
    {"id": "pf_21_alc", "nome": "PF 21% ALC", "descricao": "Preço de fábrica 21% ALC", "obrigatorio": False},
    {"id": "pf_22", "nome": "PF 22%", "descricao": "Preço de fábrica 22%", "obrigatorio": False},
    {"id": "pf_22_alc", "nome": "PF 22% ALC", "descricao": "Preço de fábrica 22% ALC", "obrigatorio": False},
    {"id": "pmc_sem_imposto", "nome": "PMC Sem Imposto", "descricao": "Preço máximo ao consumidor sem impostos", "obrigatorio": False},
    {"id": "pmc_0", "nome": "PMC 0%", "descricao": "Preço máximo ao consumidor 0%", "obrigatorio": False},
    {"id": "pmc_12", "nome": "PMC 12%", "descricao": "Preço máximo ao consumidor 12%", "obrigatorio": False},
    {"id": "pmc_12_alc", "nome": "PMC 12% ALC", "descricao": "Preço máximo ao consumidor 12% ALC", "obrigatorio": False},
    {"id": "pmc_17", "nome": "PMC 17%", "descricao": "Preço máximo ao consumidor 17%", "obrigatorio": False},
    {"id": "pmc_17_alc", "nome": "PMC 17% ALC", "descricao": "Preço máximo ao consumidor 17% ALC", "obrigatorio": False},
    {"id": "pmc_17_5", "nome": "PMC 17,5%", "descricao": "Preço máximo ao consumidor 17,5%", "obrigatorio": False},
    {"id": "pmc_17_5_alc", "nome": "PMC 17,5% ALC", "descricao": "Preço máximo ao consumidor 17,5% ALC", "obrigatorio": False},
    {"id": "pmc_18", "nome": "PMC 18%", "descricao": "Preço máximo ao consumidor 18%", "obrigatorio": False},
    {"id": "pmc_18_alc", "nome": "PMC 18% ALC", "descricao": "Preço máximo ao consumidor 18% ALC", "obrigatorio": False},
    {"id": "pmc_19", "nome": "PMC 19%", "descricao": "Preço máximo ao consumidor 19%", "obrigatorio": False},
    {"id": "pmc_19_alc", "nome": "PMC 19% ALC", "descricao": "Preço máximo ao consumidor 19% ALC", "obrigatorio": False},
    {"id": "pmc_19_5", "nome": "PMC 19,5%", "descricao": "Preço máximo ao consumidor 19,5%", "obrigatorio": False},
    {"id": "pmc_19_5_alc", "nome": "PMC 19,5% ALC", "descricao": "Preço máximo ao consumidor 19,5% ALC", "obrigatorio": False},
    {"id": "pmc_20", "nome": "PMC 20%", "descricao": "Preço máximo ao consumidor 20%", "obrigatorio": False},
    {"id": "pmc_20_alc", "nome": "PMC 20% ALC", "descricao": "Preço máximo ao consumidor 20% ALC", "obrigatorio": False},
    {"id": "pmc_20_5", "nome": "PMC 20,5%", "descricao": "Preço máximo ao consumidor 20,5%", "obrigatorio": False},
    {"id": "pmc_21", "nome": "PMC 21%", "descricao": "Preço máximo ao consumidor 21%", "obrigatorio": False},
    {"id": "pmc_21_alc", "nome": "PMC 21% ALC", "descricao": "Preço máximo ao consumidor 21% ALC", "obrigatorio": False},
    {"id": "pmc_22", "nome": "PMC 22%", "descricao": "Preço máximo ao consumidor 22%", "obrigatorio": False},
    {"id": "pmc_22_alc", "nome": "PMC 22% ALC", "descricao": "Preço máximo ao consumidor 22% ALC", "obrigatorio": False},
    {"id": "restricao_hospitalar", "nome": "Restrição Hospitalar", "descricao": "Indica se o medicamento tem restrição hospitalar", "obrigatorio": False},
    {"id": "cap", "nome": "CAP", "descricao": "Coeficiente de Adequação de Preços", "obrigatorio": False},
    {"id": "confaz_87", "nome": "CONFAZ 87", "descricao": "Convênio CONFAZ 87", "obrigatorio": False},
    {"id": "icms_0", "nome": "ICMS 0%", "descricao": "Indica se o medicamento tem ICMS 0%", "obrigatorio": False},
    {"id": "analise_recursal", "nome": "Análise Recursal", "descricao": "Indica se o medicamento está em análise recursal", "obrigatorio": False},
    {"id": "lista_concessao_credito", "nome": "Lista de Concessão de Crédito", "descricao": "Indica se o medicamento está na lista de concessão de crédito", "obrigatorio": False},
    {"id": "comercializacao_2022", "nome": "Comercialização 2022", "descricao": "Indica se o medicamento foi comercializado em 2022", "obrigatorio": False},
    {"id": "tarja", "nome": "Tarja", "descricao": "Classificação da tarja do medicamento", "obrigatorio": False}
]

# Função para salvar dados temporários entre sessões
def salvar_dados_temp(session_id, dados):
    os.makedirs('temp_data', exist_ok=True)
    with open(f'temp_data/{session_id}.pkl', 'wb') as f:
        pickle.dump(dados, f)

# Função para carregar dados temporários
def carregar_dados_temp(session_id):
    try:
        with open(f'temp_data/{session_id}.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        return None

# Função para gerar ID de sessão único
def gerar_session_id():
    return str(uuid.uuid4())

# Função auxiliar para ler arquivos Excel com diferentes engines
def ler_arquivo_excel(caminho_arquivo):
    """
    Tenta ler um arquivo Excel usando diferentes engines.
    Retorna um DataFrame pandas.
    """
    engines = ['xlrd', 'openpyxl']
    
    for engine in engines:
        try:
            if engine == 'xlrd' and caminho_arquivo.lower().endswith('.xlsx'):
                # xlrd não suporta .xlsx a partir da versão 2.0.0
                continue
                
            print(f"Tentando ler arquivo Excel com engine: {engine}")
            return pd.read_excel(caminho_arquivo, engine=engine)
        except Exception as e:
            print(f"Erro ao ler com {engine}: {str(e)}")
            continue
    
    # Se chegou aqui, nenhum engine funcionou
    raise ValueError(f"Não foi possível ler o arquivo Excel. Certifique-se de que xlrd (para .xls) ou openpyxl (para .xlsx) estão instalados.")

# Template HTML para a interface web
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Histórico de Preços de Medicamentos - CMED</title>
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
        .nav-tabs {
            margin-bottom: 20px;
        }
        .table-responsive {
            margin-top: 20px;
        }
        .alert {
            margin-top: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .tab-pane {
            padding: 20px 0;
        }
        .nav-link {
            cursor: pointer;
        }
        .import-options {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        .option-tabs {
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Histórico de Preços de Medicamentos - CMED</h1>
        </div>
        
        <ul class="nav nav-tabs">
            <li class="nav-item">
                <a class="nav-link {{ 'active' if active_tab == 'visualizacao' else '' }}" href="/">📊 Visualização de Dados</a>
            </li>
            <li class="nav-item">
                <a class="nav-link {{ 'active' if active_tab == 'importacao' else '' }}" href="/importacao">📥 Importação de Dados</a>
            </li>
            <li class="nav-item">
                <a class="nav-link {{ 'active' if active_tab == 'listar' else '' }}" href="/listar_medicamentos">📝 Listar Medicamentos</a>
            </li>
        </ul>
        
        {% if active_tab == 'visualizacao' %}
        <div class="tab-pane">
            <h2>Visualização de Dados</h2>
            <p>Esta aba permite visualizar os dados importados da CMED.</p>
            
            <div class="alert alert-info">
                Funcionalidade em desenvolvimento.
            </div>
        </div>
        {% elif active_tab == 'importacao' %}
        <div class="tab-pane">
            <h2>Importação de Dados</h2>
            <p>Esta aba permite importar arquivos da CMED para o banco de dados.</p>
            
            <div class="card">
                <div class="card-header">
                    <h3>Informações do Ambiente</h3>
                </div>
                <div class="card-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Variável</th>
                                <th>Valor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for var, value in env_vars.items() %}
                            <tr>
                                <td>{{ var }}</td>
                                <td>{{ value }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="card mt-4">
                <div class="card-header">
                    <h3>Upload de Arquivo</h3>
                </div>
                <div class="card-body">
                    <div class="import-options">
                        <ul class="nav nav-pills option-tabs" id="importOptions" role="tablist">
                            <li class="nav-item" role="presentation">
                                <button class="nav-link active" id="upload-tab" data-bs-toggle="tab" data-bs-target="#upload-content" type="button" role="tab" aria-controls="upload-content" aria-selected="true">Upload de Arquivo Local</button>
                            </li>
                            <li class="nav-item" role="presentation">
                                <button class="nav-link" id="drive-tab" data-bs-toggle="tab" data-bs-target="#drive-content" type="button" role="tab" aria-controls="drive-content" aria-selected="false">Link do Google Drive</button>
                            </li>
                        </ul>
                        
                        <div class="tab-content" id="importOptionsContent">
                            <div class="tab-pane fade show active" id="upload-content" role="tabpanel" aria-labelledby="upload-tab">
                                <form action="/upload" method="post" enctype="multipart/form-data">
                                    <div class="form-group">
                                        <label for="file">Selecione um arquivo da CMED (Excel, CSV ou DOC)</label>
                                        <input type="file" class="form-control" id="file" name="file">
                                    </div>
                                    <button type="submit" class="btn btn-primary">Enviar</button>
                                </form>
                            </div>
                            
                            <div class="tab-pane fade" id="drive-content" role="tabpanel" aria-labelledby="drive-tab">
                                <form action="/upload_from_drive" method="post">
                                    <div class="form-group">
                                        <label for="drive_link">Link do Google Drive</label>
                                        <input type="text" class="form-control" id="drive_link" name="drive_link" placeholder="https://drive.google.com/file/d/XXXX/view?usp=sharing">
                                        <small class="form-text text-muted">Cole o link de compartilhamento do arquivo no Google Drive.</small>
                                    </div>
                                    <button type="submit" class="btn btn-primary">Importar do Drive</button>
                                </form>
                            </div>
                        </div>
                    </div>
                    
                    <div class="mt-3">
                        <h4>Formatos suportados:</h4>
                        <ul>
                            <li>Excel (.xlsx, .xls) - Arquivos padrão da CMED</li>
                            <li>CSV (.csv) - Arquivos de texto separados por vírgulas</li>
                            <li>DOC (.doc) - Arquivos antigos no formato "json-file-1.doc"</li>
                        </ul>
                    </div>
                </div>
            </div>
            
            {% if message %}
            <div class="alert alert-{{ 'success' if message_type == 'success' else 'danger' }} mt-4">
                {{ message|safe }}
            </div>
            {% endif %}
            
            {% if preview_data %}
            <div class="card mt-4">
                <div class="card-header">
                    <h3>Prévia dos Dados</h3>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    {% for col in preview_columns %}
                                    <th>{{ col }}</th>
                                    {% endfor %}
                                </tr>
                            </thead>
                            <tbody>
                                {% for row in preview_data %}
                                <tr>
                                    {% for cell in row %}
                                    <td>{{ cell }}</td>
                                    {% endfor %}
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>
        {% elif active_tab == 'listar' %}
        <div class="tab-pane">
            <h2>Listar Medicamentos</h2>
            <p>Esta aba permite visualizar os medicamentos cadastrados no Supabase.</p>
            
            {% if dados %}
            <div class="table-responsive">
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Substância</th>
                            <th>Laboratório</th>
                            <th>Produto</th>
                            <th>Apresentação</th>
                            <th>PF Sem Impostos</th>
                            <th>Data de Publicação</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for dado in dados %}
                        <tr>
                            <td>{{ dado.id }}</td>
                            <td>{{ dado.substancia }}</td>
                            <td>{{ dado.laboratorio }}</td>
                            <td>{{ dado.produto }}</td>
                            <td>{{ dado.apresentacao }}</td>
                            <td>{{ dado.pf_sem_impostos }}</td>
                            <td>{{ dado.data_publicacao }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% else %}
            <div class="alert alert-info">
                Nenhum medicamento encontrado no banco de dados.
            </div>
            {% endif %}
        </div>
        {% endif %}
        
        <footer class="mt-5 pt-3 text-muted border-top">
            <p>Dados obtidos da tabela CMED (Câmara de Regulação do Mercado de Medicamentos)</p>
        </footer>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Template HTML para a página de mapeamento de colunas
TEMPLATE_MAPEAMENTO = '''
{% extends 'base_template' %}

{% block content %}
<div class="container py-4">
    <h2>Mapeamento de Colunas</h2>
    <p>Arquivo: {{ arquivo_original }}</p>
    
    {% if message %}
    <div class="alert alert-{{ 'success' if message_type == 'success' else 'danger' }}" role="alert">
        {{ message }}
    </div>
    {% endif %}
    
    <div id="loading" class="alert alert-info" style="display: none;">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Carregando...</span>
        </div>
        <span class="ms-2">Processando o mapeamento, por favor aguarde...</span>
    </div>
    
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    Prévia dos Dados
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped table-sm">
                            <thead>
                                <tr>
                                    {% for col in preview_columns %}
                                    <th>{{ col }}</th>
                                    {% endfor %}
                                </tr>
                            </thead>
                            <tbody>
                                {% for row in preview_data %}
                                <tr>
                                    {% for col in preview_columns %}
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
    
    <h3>Mapeamento de Colunas</h3>
    <p>Selecione a coluna do arquivo que corresponde a cada campo do sistema. Os campos marcados com * são obrigatórios.</p>
    
    <form id="mappingForm" action="{{ url_for('mapear_colunas', session_id=session_id) }}" method="post">
        <div class="row">
            {% for campo in campos_necessarios %}
            <div class="col-md-6 mb-3">
                <label for="campo_{{ campo.id }}">{{ campo.nome }}{% if campo.obrigatorio %} *{% endif %}</label>
                <select class="form-select" name="campo_{{ campo.id }}" id="campo_{{ campo.id }}">
                    <option value="nenhum">-- Selecione uma coluna --</option>
                    {% for coluna in colunas_arquivo %}
                    <option value="{{ coluna }}" {% if mapeamento_sugerido and mapeamento_sugerido.get(campo.id) == coluna %}selected{% endif %}>{{ coluna }}</option>
                    {% endfor %}
                </select>
                <small class="form-text text-muted">{{ campo.descricao }}</small>
            </div>
            {% endfor %}
        </div>
        
        <div class="d-grid gap-2 d-md-flex justify-content-md-end mt-4">
            <button type="submit" class="btn btn-primary" onclick="showLoading()">Confirmar Mapeamento</button>
        </div>
    </form>
</div>

<script>
function showLoading() {
    // Validar campos obrigatórios antes de mostrar o loading
    var form = document.getElementById('mappingForm');
    if (form.checkValidity()) {
        document.getElementById('loading').style.display = 'block';
    }
}
</script>
{% endblock %}
'''

# Template HTML para a página de confirmação de importação
TEMPLATE_CONFIRMACAO = '''
{% extends 'base_template' %}

{% block content %}
<div class="container py-4">
    <h2>Confirmar Importação</h2>
    <p>Arquivo: {{ arquivo_original }}</p>
    
    {% if message %}
    <div class="alert alert-{{ 'success' if message_type == 'success' else 'danger' }}" role="alert">
        {{ message }}
    </div>
    {% endif %}
    
    <div id="loading" class="alert alert-info" style="display: none;">
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Carregando...</span>
        </div>
        <span class="ms-2">Processando a importação, por favor aguarde. Isso pode levar alguns minutos...</span>
    </div>
    
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    Prévia dos Dados
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-striped table-sm">
                            <thead>
                                <tr>
                                    {% for col in df_preview.columns %}
                                    <th>{{ col }}</th>
                                    {% endfor %}
                                </tr>
                            </thead>
                            <tbody>
                                {% for _, row in df_preview.iterrows() %}
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
    
    <h3>Mapeamento de Colunas</h3>
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    Campos Mapeados
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
                            {% for campo in campos_necessarios %}
                            <tr>
                                <td>{{ campo.nome }}{% if campo.obrigatorio %} *{% endif %}</td>
                                <td>
                                    {% if campo.id in mapeamento %}
                                    {{ mapeamento[campo.id] }}
                                    {% else %}
                                    <span class="text-muted">Não mapeado</span>
                                    {% endif %}
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    
    <form id="importForm" action="{{ url_for('confirmar_importacao', session_id=session_id) }}" method="post" class="mb-4">
        <div class="mb-3">
            <label for="data_publicacao" class="form-label">Data de Publicação *</label>
            <input type="date" class="form-control" id="data_publicacao" name="data_publicacao" required>
            <div class="form-text">Data de publicação da tabela CMED</div>
        </div>
        
        <div class="d-grid gap-2 d-md-flex justify-content-md-end">
            <button type="submit" class="btn btn-primary" onclick="showLoading()">Confirmar Importação</button>
        </div>
    </form>
</div>

<script>
function showLoading() {
    // Validar campos obrigatórios antes de mostrar o loading
    var form = document.getElementById('importForm');
    if (form.checkValidity()) {
        document.getElementById('loading').style.display = 'block';
    }
}
</script>
{% endblock %}
'''

# Template base para as páginas
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Histórico de Preços de Medicamentos - CMED</title>
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
        .nav-tabs {
            margin-bottom: 20px;
        }
        .table-responsive {
            margin-top: 20px;
        }
        .alert {
            margin-top: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .tab-pane {
            padding: 20px 0;
        }
        .nav-link {
            cursor: pointer;
        }
        .import-options {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        .option-tabs {
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        {% block content %}{% endblock %}
        
        <footer class="mt-5 pt-3 text-muted border-top">
            <p>Dados obtidos da tabela CMED (Câmara de Regulação do Mercado de Medicamentos)</p>
        </footer>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

# Template HTML para a página de listagem de medicamentos
TEMPLATE_LISTAR_MEDICAMENTOS = '''
{% extends 'base_template' %}

{% block content %}
<div class="container py-4">
    <h2>Listar Medicamentos</h2>
    <p>Esta aba permite visualizar os medicamentos cadastrados no Supabase.</p>
    
    {% if message %}
    <div class="alert alert-{{ 'success' if message_type == 'success' else 'danger' }}" role="alert">
        {{ message }}
    </div>
    {% endif %}
    
    {% if dados %}
    <div class="table-responsive">
        <table class="table table-striped">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Substância</th>
                    <th>Laboratório</th>
                    <th>Produto</th>
                    <th>Apresentação</th>
                    <th>PF Sem Impostos</th>
                    <th>Data de Publicação</th>
                </tr>
            </thead>
            <tbody>
                {% for dado in dados %}
                <tr>
                    <td>{{ dado.id }}</td>
                    <td>{{ dado.substancia }}</td>
                    <td>{{ dado.laboratorio }}</td>
                    <td>{{ dado.produto }}</td>
                    <td>{{ dado.apresentacao }}</td>
                    <td>{{ dado.pf_sem_impostos }}</td>
                    <td>{{ dado.data_publicacao }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% else %}
    <div class="alert alert-info">
        Nenhum medicamento encontrado no banco de dados.
    </div>
    {% endif %}
</div>
{% endblock %}
'''

# Função para inicializar a conexão com o Supabase
def init_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos no arquivo .env")
    return create_client(url, key)

# Função para serializar valores para JSON
def serializar_para_json(valor):
    """Serializa um valor para formato compatível com JSON"""
    if isinstance(valor, (datetime.date, datetime.datetime)):
        return valor.isoformat()
    elif pd.isna(valor) or valor is None:
        return None
    elif isinstance(valor, (int, float)):
        if math.isnan(valor) or math.isinf(valor):
            return None
        return valor
    elif isinstance(valor, bool):
        return valor
    elif isinstance(valor, str):
        if valor.strip() == '':
            return None
        return valor
    return str(valor)

# Função para converter valores para booleano
def converter_para_booleano(valor):
    """Converte um valor para booleano"""
    if pd.isna(valor) or valor is None or valor == '':
        return None
    
    if isinstance(valor, bool):
        return valor
    
    if isinstance(valor, (int, float)):
        if math.isnan(valor) or math.isinf(valor):
            return None
        return bool(valor)
    
    if isinstance(valor, str):
        valor = valor.lower().strip()
        if valor in ('sim', 's', 'true', '1', 'yes', 'y'):
            return True
        if valor in ('não', 'nao', 'n', 'false', '0', 'no'):
            return False
        return None
    
    return None

# Função para salvar dados no Supabase
def salvar_no_supabase(df, data_publicacao):
    """
    Salva os dados no Supabase
    """
    try:
        print("="*80)
        print("INICIANDO SALVAR NO SUPABASE")
        print(f"Colunas no DataFrame: {df.columns.tolist()}")
        print(f"Total de linhas no DataFrame: {len(df)}")
        print("="*80)
        
        # Garantir que todos os nomes de colunas estejam em minúsculas
        df.columns = [col.lower() for col in df.columns]
        
        # Mostrar os valores da coluna substancia para debug
        if 'substancia' in df.columns:
            print("="*50)
            print("Valores da coluna 'substancia':")
            print(df['substancia'].head(5).tolist())
            print("="*50)
        
        # Verificar conexão com Supabase
        supabase = init_supabase()
        try:
            # Testar a conexão
            print("Testando conexão com Supabase...")
            response = supabase.table('medicamentos').select('count', count='exact').limit(1).execute()
            print(f"Conexão testada: {response}")
        except Exception as e:
            print(f"ERRO ao testar conexão com Supabase: {str(e)}")
            raise Exception(f"Falha na conexão com Supabase: {str(e)}")
        
        # Verificar se o DataFrame está vazio
        if df.empty:
            print("ERRO: DataFrame está vazio!")
            raise ValueError("DataFrame está vazio, não há dados para importar")

        # VALIDAÇÃO CRÍTICA: Verificar a contagem atual de registros para comparação posterior
        try:
            contagem_antes = 0
            resp_contagem = supabase.table('medicamentos').select('count', count='exact').execute()
            if resp_contagem and hasattr(resp_contagem, 'count'):
                contagem_antes = resp_contagem.count
            print(f"Contagem de registros ANTES da importação: {contagem_antes}")
        except Exception as e:
            print(f"Aviso: Não foi possível obter contagem inicial: {str(e)}")
        
        # Converter os tipos de dados
        # Converter colunas numéricas
        colunas_numericas = [
            'pf_sem_impostos', 'pf_0', 'pf_12', 'pf_12_alc', 'pf_17', 'pf_17_alc',
            'pf_17_5', 'pf_17_5_alc', 'pf_18', 'pf_18_alc', 'pf_19', 'pf_19_alc',
            'pf_19_5', 'pf_19_5_alc', 'pf_20', 'pf_20_alc', 'pf_20_5', 'pf_21',
            'pf_21_alc', 'pf_22', 'pf_22_alc', 'pmc_sem_imposto', 'pmc_0', 'pmc_12',
            'pmc_12_alc', 'pmc_17', 'pmc_17_alc', 'pmc_17_5', 'pmc_17_5_alc', 'pmc_18',
            'pmc_18_alc', 'pmc_19', 'pmc_19_alc', 'pmc_19_5', 'pmc_19_5_alc', 'pmc_20',
            'pmc_20_alc', 'pmc_20_5', 'pmc_21', 'pmc_21_alc', 'pmc_22', 'pmc_22_alc'
        ]
        
        for col in colunas_numericas:
            if col in df.columns:
                print(f"Convertendo coluna numérica: {col}")
                
                # Tentar diferentes métodos de conversão
                try:
                    if isinstance(df[col], pd.Series) and df[col].dtype == object:
                        df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='coerce')
                    else:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                except Exception as e:
                    print(f"Erro ao converter coluna {col}: {str(e)}")
        
        # Converter colunas booleanas
        colunas_booleanas = ['restricao_hospitalar', 'cap', 'confaz_87', 'icms_0', 
                            'analise_recursal', 'lista_concessao_credito', 'comercializacao_2022']
        for col in colunas_booleanas:
            if col in df.columns:
                print(f"Convertendo coluna booleana: {col}")
                # Converter cada valor usando a função converter_para_booleano
                df[col] = df[col].apply(converter_para_booleano)
        
        # Adicionar a data de publicação
        df['data_publicacao'] = data_publicacao
        
        # CORREÇÃO: Garantir que o campo regime_de_preco esteja corretamente mapeado
        if 'regime_preco' in df.columns and 'regime_de_preco' not in df.columns:
            df['regime_de_preco'] = df['regime_preco']
            print("Corrigido: campo 'regime_preco' mapeado para 'regime_de_preco'")
            
        if 'tipo_produto' in df.columns and 'tipo_de_produto' not in df.columns:
            df['tipo_de_produto'] = df['tipo_produto']
            print("Corrigido: campo 'tipo_produto' mapeado para 'tipo_de_produto'")
        
        # Converter o DataFrame para uma lista de dicionários
        registros = []
        for idx, row in df.iterrows():
            registro = {}
            for coluna in df.columns:
                valor = row[coluna]
                # Serializar o valor para JSON
                registro[coluna] = serializar_para_json(valor)
            registros.append(registro)
        
        print(f"Total de registros a serem inseridos: {len(registros)}")
        if registros:
            print("Exemplo do primeiro registro:")
            print(json.dumps(registros[0], indent=2, ensure_ascii=False))
        else:
            print("ALERTA: Nenhum registro para inserir!")
            return 0
        
        # Verificar a estrutura da tabela
        try:
            # Obter a estrutura da tabela 'medicamentos'
            print("Verificando a estrutura da tabela 'medicamentos'...")
            response = supabase.table('medicamentos').select('count').limit(1).execute()
            print(f"Estrutura da tabela verificada: {response}")
        except Exception as e:
            print(f"AVISO: Erro ao verificar estrutura da tabela: {str(e)}")
            # Continuar mesmo se não conseguir verificar a estrutura
        
        # MÉTODO ALTERNATIVO - Preparando os registros
        print("Preparando registros para inserção...")
        # Garantir que todos os registros tenham pelo menos o campo 'substancia'
        for registro in registros:
            if 'substancia' not in registro or not registro['substancia']:
                registro['substancia'] = 'NÃO ESPECIFICADO'
        
        # Limpar registros existentes para evitar duplicações
        try:
            print("Limpando registros existentes com a mesma data...")
            data_str = data_publicacao.isoformat() if hasattr(data_publicacao, 'isoformat') else str(data_publicacao)
            delete_response = supabase.table('medicamentos').delete().eq('data_publicacao', data_str).execute()
            print(f"Resposta da limpeza: {delete_response}")
        except Exception as e:
            print(f"Aviso: Não foi possível limpar registros antigos: {str(e)}")
        
        # MODIFICAÇÃO: Usar RPC para inserção em massa
        try:
            print("Tentando usar RPC para inserção em massa...")
            url = f"{os.getenv('SUPABASE_URL')}/rest/v1/rpc/importar_medicamentos_em_massa"
            headers = {
                "apikey": os.getenv('SUPABASE_KEY'),
                "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            }
            payload = {
                "registros": registros
            }
            
            try:
                response = requests.post(url, headers=headers, json=payload)
                print(f"Resposta RPC: Status {response.status_code}")
                print(f"Conteúdo: {response.text[:1000]}...")  # Mostrar primeiros 1000 caracteres
                
                if response.status_code in (200, 201, 204):
                    print("Importação em massa via RPC bem-sucedida")
                    total_registros = len(registros)
                else:
                    print("Falha na importação em massa via RPC, tentando método padrão")
                    raise Exception("Falha na RPC")
            except Exception as e:
                print(f"Erro na RPC: {str(e)}")
                raise Exception("Falha na chamada RPC")
        except Exception as e:
            print(f"RPC falhou, usando método de inserção em lotes: {str(e)}")
            
            # Inserir os registros no Supabase em lotes de 50
            tamanho_lote = 50  # Reduzir o tamanho do lote para evitar problemas
            total_registros = 0
            
            # MODIFICAÇÃO: Dividir em lotes ainda menores se tivermos muitos registros
            if len(registros) > 1000:
                tamanho_lote = 20
                print(f"Muitos registros detectados ({len(registros)}), reduzindo tamanho do lote para {tamanho_lote}")
            
            for i in range(0, len(registros), tamanho_lote):
                lote = registros[i:i + tamanho_lote]
                print(f"Processando lote {i//tamanho_lote + 1} com {len(lote)} registros")
                try:
                    print("Enviando lote para o Supabase...")
                    response = supabase.table('medicamentos').insert(lote).execute()
                    data = response.data
                    print(f"Resposta do Supabase: {data if data else 'Sem dados'}")
                    total_registros += len(lote)
                    print(f"Lote {i//tamanho_lote + 1} processado com sucesso: {len(lote)} registros")
                except Exception as e:
                    print(f"Erro ao processar lote {i//tamanho_lote + 1}: {str(e)}")
                    if hasattr(e, 'args') and len(e.args) > 0:
                        print(f"Detalhes do erro: {e.args}")
                    if hasattr(e, '__dict__'):
                        print(f"Atributos do erro: {e.__dict__}")
                    # Tentar inserir um a um para identificar registros problemáticos
                    print("Tentando inserir registros individualmente...")
                    for j, registro in enumerate(lote):
                        try:
                            supabase.table('medicamentos').insert(registro).execute()
                            total_registros += 1
                            print(f"Registro {j+1} inserido com sucesso")
                        except Exception as e2:
                            print(f"Erro ao inserir registro {j+1}: {str(e2)}")
        
        # VALIDAÇÃO CRÍTICA: Verificar se os registros foram realmente salvos
        try:
            contagem_depois = 0
            resp_contagem = supabase.table('medicamentos').select('count', count='exact').execute()
            if resp_contagem and hasattr(resp_contagem, 'count'):
                contagem_depois = resp_contagem.count
            print(f"Contagem de registros APÓS a importação: {contagem_depois}")
            print(f"Diferença de registros: {contagem_depois - contagem_antes}")
            
            if contagem_depois <= contagem_antes:
                print("ALERTA CRÍTICO: Nenhum registro novo foi adicionado!")
                if total_registros > 0:
                    print("INCONSISTÊNCIA DETECTADA: Sistema reportou inserção mas contagem não aumentou")
                    # Uma possibilidade é que os registros foram aceitos mas a RLS está impedindo de vê-los
                    # Tentar buscar registros específicos para esta data
                    data_str = data_publicacao.isoformat() if hasattr(data_publicacao, 'isoformat') else str(data_publicacao)
                    verificar = supabase.table('medicamentos').select('count', count='exact').eq('data_publicacao', data_str).execute()
                    print(f"Tentativa de verificar por data: {verificar}")
            else:
                print(f"VERIFICAÇÃO BEM-SUCEDIDA: {contagem_depois - contagem_antes} novos registros confirmados")
        except Exception as e:
            print(f"Aviso: Não foi possível verificar contagem final: {str(e)}")
        
        print(f"Total de registros importados: {total_registros}")
        return total_registros
        
    except Exception as e:
        print(f"Erro ao salvar no Supabase: {str(e)}")
        if hasattr(e, 'args') and len(e.args) > 0:
            print(f"Detalhes do erro: {e.args}")
        traceback.print_exc()
        raise e

@app.route('/')
def index():
    # Carregar variáveis de ambiente
    env_vars = {
        'SUPABASE_URL': '✓ Definido' if os.getenv('SUPABASE_URL') else '✗ Não definido',
        'SUPABASE_KEY': '✓ Definido' if os.getenv('SUPABASE_KEY') else '✗ Não definido'
    }
    
    return render_template_string(HTML_TEMPLATE, 
                                 active_tab='visualizacao', 
                                 env_vars=env_vars,
                                 message=None,
                                 message_type=None,
                                 preview_data=None,
                                 preview_columns=None)

@app.route('/importacao')
def importacao():
    return render_template_string(HTML_TEMPLATE, 
                                 active_tab='importacao', 
                                 env_vars={
                                     'SUPABASE_URL': '✓ Definido' if os.getenv('SUPABASE_URL') else '✗ Não definido',
                                     'SUPABASE_KEY': '✓ Definido' if os.getenv('SUPABASE_KEY') else '✗ Não definido'
                                 },
                                 message='Selecione um arquivo da CMED para importar (Excel, CSV ou DOC)',
                                 message_type='info',
                                 preview_data=None,
                                 preview_columns=None)

@app.route('/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Nome de arquivo vazio'}), 400
        
        # Verificar extensão do arquivo
        if not file.filename.lower().endswith(('.xlsx', '.xls', '.doc', '.csv')):
            return jsonify({'error': 'Formato de arquivo não suportado. Use arquivos Excel (.xlsx, .xls), CSV (.csv) ou DOC (.doc)'}), 400
        
        # Criar diretório temporário se não existir
        os.makedirs('temp_uploads', exist_ok=True)
        os.makedirs('temp_data', exist_ok=True)
        
        # Gerar um ID de sessão único
        session_id = gerar_session_id()
        
        # Salvar o arquivo temporariamente com nome único para evitar conflitos
        filename = secure_filename(file.filename)
        temp_path = os.path.join('temp_uploads', f"{session_id}_{filename}")
        file.save(temp_path)
        
        # Processar o arquivo
        if file.filename.lower().endswith(('.xlsx', '.xls')):
            # Processar arquivo Excel
            df = ler_arquivo_excel(temp_path)
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
        elif file.filename.lower().endswith('.doc'):
            # Processar arquivo .doc (assumindo que é um JSON)
            with open(temp_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    df = pd.DataFrame(data)
                except json.JSONDecodeError:
                    raise ValueError("O conteúdo do arquivo não parece ser JSON válido")
        else:
            raise ValueError(f"Formato de arquivo não suportado: {file.filename}. Use arquivos Excel (.xlsx, .xls), CSV (.csv) ou DOC (.doc)")
        
        # Salvar os dados temporariamente
        dados_temp = {
            'df': df,
            'colunas': df.columns.tolist(),
            'arquivo_original': file.filename,
            'temp_path': temp_path  # Armazenar o caminho do arquivo temporário
        }
        
        salvar_dados_temp(session_id, dados_temp)
        
        # Redirecionar para a página de mapeamento de colunas
        return redirect(url_for('mapear_colunas', session_id=session_id))
        
    except Exception as e:
        import traceback
        traceback_str = traceback.format_exc()
        print(f"Erro ao processar upload: {str(e)}")
        print(f"Traceback: {traceback_str}")
        
        # Tentar limpar arquivo temporário se existir
        if 'temp_path' in locals():
            try:
                os.remove(temp_path)
            except:
                pass
                
        return jsonify({'error': str(e)}), 500

@app.route('/upload_from_drive', methods=['POST'])
def upload_from_drive():
    try:
        drive_url = request.form.get('drive_url', '')
        
        if not drive_url:
            return render_template_string(HTML_TEMPLATE, 
                                         active_tab='importacao', 
                                         env_vars={
                                             'SUPABASE_URL': '✓ Definido' if os.getenv('SUPABASE_URL') else '✗ Não definido',
                                             'SUPABASE_KEY': '✓ Definido' if os.getenv('SUPABASE_KEY') else '✗ Não definido'
                                         },
                                         message='URL do Google Drive não fornecida',
                                         message_type='error',
                                         preview_data=None,
                                         preview_columns=None)
        
        # Extrair o ID do arquivo do Google Drive
        drive_id = None
        
        # Padrão para URLs compartilhadas do Google Drive
        if 'drive.google.com/file/d/' in drive_url:
            drive_id = drive_url.split('drive.google.com/file/d/')[1].split('/')[0]
        # Padrão para URLs de visualização do Google Drive
        elif 'drive.google.com/open?id=' in drive_url:
            drive_id = drive_url.split('drive.google.com/open?id=')[1].split('&')[0]
        
        if not drive_id:
            return render_template_string(HTML_TEMPLATE, 
                                         active_tab='importacao', 
                                         env_vars={
                                             'SUPABASE_URL': '✓ Definido' if os.getenv('SUPABASE_URL') else '✗ Não definido',
                                             'SUPABASE_KEY': '✓ Definido' if os.getenv('SUPABASE_KEY') else '✗ Não definido'
                                         },
                                         message='Não foi possível extrair o ID do arquivo do Google Drive',
                                         message_type='error',
                                         preview_data=None,
                                         preview_columns=None)
        
        # Criar diretório temporário
        os.makedirs('temp_uploads', exist_ok=True)
        os.makedirs('temp_data', exist_ok=True)
        
        # Gerar um ID de sessão único
        session_id = gerar_session_id()
        
        # Nome do arquivo temporário
        temp_path = os.path.join('temp_uploads', f"{session_id}_drive_file")
        
        # Baixar o arquivo do Google Drive
        import gdown
        gdown.download(f"https://drive.google.com/uc?id={drive_id}", temp_path, quiet=False)
        
        # Tentar determinar o tipo de arquivo
        import magic
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(temp_path)
        
        # Determinar a extensão com base no tipo MIME
        file_ext = None
        if 'excel' in file_type or 'spreadsheet' in file_type:
            if 'xls' in file_type and 'xlsx' not in file_type:
                file_ext = '.xls'
            else:
                file_ext = '.xlsx'
        elif 'msword' in file_type:
            file_ext = '.doc'
        else:
            raise ValueError(f"Formato de arquivo não suportado: {file_ext}. Use arquivos Excel (.xlsx, .xls), CSV (.csv) ou DOC (.doc)")
        
        # Renomear o arquivo com a extensão correta
        new_temp_path = temp_path + file_ext
        os.rename(temp_path, new_temp_path)
        temp_path = new_temp_path
        
        # Processar o arquivo de acordo com a extensão
        if file_ext.lower() in ['.xlsx', '.xls']:
            # Ler o arquivo Excel
            df = ler_arquivo_excel(temp_path)
        elif file_ext.lower() == '.csv':
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
        elif file_ext.lower() == '.doc':
            # Processar arquivo .doc (formato antigo)
            print(f"Processando arquivo .doc do Google Drive: {temp_path}")
            
            # Ler o arquivo como texto simples
            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"Conteúdo do arquivo (primeiros 100 caracteres): {content[:100]}")
            
            # Tentar carregar como JSON
            try:
                data = json.loads(content)
                is_valid_json = True
                print("JSON carregado com sucesso")
            except json.JSONDecodeError:
                # Limpar arquivo temporário
                try:
                    os.remove(temp_path)
                except:
                    pass
                return jsonify({'error': 'Erro ao decodificar o arquivo JSON'}), 400
            
            if is_valid_json:
                # Verificar se temos uma estrutura específica
                if 'medicamentos' in data and isinstance(data['medicamentos'], list):
                    # Criar DataFrame a partir da lista de medicamentos
                    df = pd.DataFrame(data['medicamentos'])
                    print(f"Extraídos {len(df)} medicamentos do arquivo")
                elif 'precos' in data and isinstance(data['precos'], list):
                    # Criar DataFrame a partir da lista de preços
                    df = pd.DataFrame(data['precos'])
                    print(f"Extraídos {len(df)} registros de preços do arquivo")
                else:
                    # Tentar criar DataFrame a partir do JSON completo
                    df = pd.DataFrame([data])
                    print("Criado DataFrame a partir do JSON completo")
            else:
                raise ValueError("O conteúdo do arquivo não parece ser JSON válido")
        else:
            raise ValueError(f"Formato de arquivo não suportado: {file_ext}. Use arquivos Excel (.xlsx, .xls), CSV (.csv) ou DOC (.doc)")
        
        # Extrair o nome original do arquivo
        import requests
        response = requests.get(f"https://drive.google.com/uc?id={drive_id}&export=download", allow_redirects=False)
        content_disposition = response.headers.get('content-disposition', '')
        filename = 'arquivo_do_drive'
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].split(';')[0].strip('"\'')
        else:
            filename = f"arquivo_drive_{drive_id}{file_ext}"
        
        # Salvar os dados temporariamente
        dados_temp = {
            'df': df,
            'colunas': df.columns.tolist(),
            'arquivo_original': filename,
            'temp_path': temp_path  # Armazenar o caminho do arquivo temporário
        }
        
        salvar_dados_temp(session_id, dados_temp)
        
        # Redirecionar para a página de mapeamento
        return redirect(url_for('mapear_colunas', session_id=session_id))
        
    except Exception as e:
        import traceback
        print(f"Erro ao processar arquivo do Google Drive: {str(e)}")
        print(traceback.format_exc())
        
        # Limpar arquivos temporários se existirem
        if 'temp_path' in locals() and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        
        return render_template_string(HTML_TEMPLATE, 
                                     active_tab='importacao', 
                                     env_vars={
                                         'SUPABASE_URL': '✓ Definido' if os.getenv('SUPABASE_URL') else '✗ Não definido',
                                         'SUPABASE_KEY': '✓ Definido' if os.getenv('SUPABASE_KEY') else '✗ Não definido'
                                     },
                                     message=f'Erro ao processar o arquivo do Google Drive: {str(e)}',
                                     message_type='error',
                                     preview_data=None,
                                     preview_columns=None)

@app.route('/mapear_colunas/<session_id>', methods=['GET', 'POST'])
def mapear_colunas(session_id):
    # Carregar dados temporários
    dados_temp = carregar_dados_temp(session_id)
    
    if not dados_temp:
        return render_template_string(HTML_TEMPLATE, 
                                     active_tab='importacao', 
                                     env_vars={
                                         'SUPABASE_URL': '✓ Definido' if os.getenv('SUPABASE_URL') else '✗ Não definido',
                                         'SUPABASE_KEY': '✓ Definido' if os.getenv('SUPABASE_KEY') else '✗ Não definido'
                                     },
                                     message='Sessão expirada ou inválida. Por favor, faça o upload novamente.',
                                     message_type='error',
                                     preview_data=None,
                                     preview_columns=None)
    
    df = dados_temp['df']
    arquivo_original = dados_temp['arquivo_original']
    temp_path = dados_temp.get('temp_path')
    
    # Obter as colunas do arquivo
    colunas_arquivo = df.columns.tolist()
    
    # Criar um mapeamento sugerido
    mapeamento_sugerido = {}
    
    # Função para normalizar strings para comparação
    def normalizar_string(s):
        return re.sub(r'[^a-zA-Z0-9]', '', s.lower())
    
    # Criar um dicionário de campos normalizados para busca
    campos_normalizados = {normalizar_string(campo['nome']): campo['id'] 
                          for campo in CAMPOS_NECESSARIOS}
    
    # Para cada coluna do arquivo, tentar encontrar um campo correspondente
    for coluna in colunas_arquivo:
        coluna_normalizada = normalizar_string(coluna)
        
        # Tratamento especial para colunas EAN
        if 'ean' in coluna_normalizada:
            if '1' in coluna_normalizada or coluna_normalizada == 'ean':
                mapeamento_sugerido['ean_1'] = coluna
            elif '2' in coluna_normalizada:
                mapeamento_sugerido['ean_2'] = coluna
            elif '3' in coluna_normalizada:
                mapeamento_sugerido['ean_3'] = coluna
            continue
        
        # Buscar campo correspondente
        for nome_campo, id_campo in campos_normalizados.items():
            if coluna_normalizada == nome_campo or coluna_normalizada in nome_campo:
                mapeamento_sugerido[id_campo] = coluna
                break
    
    # Mapeamento direto para campos críticos
    for coluna in colunas_arquivo:
        coluna_lower = coluna.lower()
        if 'substância' in coluna_lower or 'substancia' in coluna_lower:
            mapeamento_sugerido['substancia'] = coluna
        elif 'cnpj' in coluna_lower:
            mapeamento_sugerido['cnpj'] = coluna
        elif 'laboratório' in coluna_lower or 'laboratorio' in coluna_lower:
            mapeamento_sugerido['laboratorio'] = coluna
    
    if request.method == 'POST':
        # Processar o formulário de mapeamento
        mapeamento = {}
        for campo in CAMPOS_NECESSARIOS:
            campo_id = campo['id']
            # Remover o prefixo 'campo_' do nome do campo no formulário
            coluna_selecionada = request.form.get(f'campo_{campo_id}')
            
            if coluna_selecionada and coluna_selecionada != 'nenhum':
                mapeamento[campo_id] = coluna_selecionada
            elif campo['obrigatorio']:
                return render_template_string(TEMPLATE_MAPEAMENTO, 
                                             session_id=session_id,
                                             arquivo_original=arquivo_original,
                                             colunas_arquivo=colunas_arquivo,
                                             campos_necessarios=CAMPOS_NECESSARIOS,
                                             preview_data=df.head().to_dict('records'),
                                             preview_columns=df.columns.tolist(),
                                             mapeamento_sugerido=mapeamento_sugerido,
                                             message=f'O campo {campo["nome"]} é obrigatório.',
                                             message_type='error')
        
        # Salvar o mapeamento nos dados temporários
        dados_temp['mapeamento'] = mapeamento
        salvar_dados_temp(session_id, dados_temp)
        
        # Redirecionar para a página de confirmação
        return redirect(url_for('confirmar_importacao', session_id=session_id))
    
    # Exibir o formulário de mapeamento
    return render_template_string(TEMPLATE_MAPEAMENTO, 
                                 session_id=session_id,
                                 arquivo_original=arquivo_original,
                                 colunas_arquivo=colunas_arquivo,
                                 campos_necessarios=CAMPOS_NECESSARIOS,
                                 preview_data=df.head().to_dict('records'),
                                 preview_columns=df.columns.tolist(),
                                 mapeamento_sugerido=mapeamento_sugerido,
                                 message=None,
                                 message_type=None)

@app.route('/confirmar_importacao/<session_id>', methods=['GET', 'POST'])
def confirmar_importacao(session_id):
    # Carregar dados temporários
    dados_temp = carregar_dados_temp(session_id)
    
    if not dados_temp or 'mapeamento' not in dados_temp:
        return render_template_string(HTML_TEMPLATE, 
                                     active_tab='importacao', 
                                     env_vars={
                                         'SUPABASE_URL': '✓ Definido' if os.getenv('SUPABASE_URL') else '✗ Não definido',
                                         'SUPABASE_KEY': '✓ Definido' if os.getenv('SUPABASE_KEY') else '✗ Não definido'
                                     },
                                     message='Sessão expirada ou inválida. Por favor, faça o upload novamente.',
                                     message_type='error',
                                     preview_data=None,
                                     preview_columns=None)
    
    df = dados_temp['df']
    mapeamento = dados_temp['mapeamento']
    arquivo_original = dados_temp['arquivo_original']
    temp_path = dados_temp.get('temp_path')
    
    # GARANTIR CAMPOS CRÍTICOS
    if 'substancia' not in mapeamento:
        # Tentar encontrar uma coluna com nome similar
        for coluna in df.columns:
            if 'subst' in coluna.lower():
                mapeamento['substancia'] = coluna
                break
    
    # Verificar o mapeamento recebido
    print("="*80)
    print(f"DETALHES DO MAPEAMENTO RECEBIDO:")
    print(f"Tipo do mapeamento: {type(mapeamento)}")
    print(f"Conteúdo do mapeamento: {mapeamento}")
    print(f"Campos mapeados: {list(mapeamento.keys())}")
    print(f"Colunas do DataFrame: {df.columns.tolist()}")
    print("="*80)
    
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
            
            # Converter a data de publicação para o formato correto
            try:
                data_publicacao = datetime.datetime.strptime(data_publicacao, '%Y-%m-%d').date()
            except ValueError as e:
                return render_template_string(TEMPLATE_CONFIRMACAO, 
                                              session_id=session_id,
                                              arquivo_original=arquivo_original,
                                              mapeamento=mapeamento,
                                              df_preview=df.head(5),
                                              campos_necessarios=CAMPOS_NECESSARIOS,
                                              message=f'Data de publicação inválida: {str(e)}',
                                              message_type='error')
            
            # Criar um novo DataFrame com as colunas mapeadas - SIMPLIFICADO
            df_mapeado = pd.DataFrame()
            
            print("="*80)
            print("INICIANDO MAPEAMENTO DE COLUNAS:")
            
            # Mapear cada coluna do arquivo para o campo correto no Supabase
            for campo_id, coluna_original in mapeamento.items():
                print(f"Mapeando {campo_id} -> {coluna_original}")
                
                # Verificar se a coluna original existe no DataFrame
                if coluna_original not in df.columns:
                    print(f"AVISO: Coluna {coluna_original} não encontrada no DataFrame! Ignorando.")
                    continue
                
                # Copiar a coluna com o novo nome no DataFrame mapeado
                df_mapeado[campo_id] = df[coluna_original]
            
            # Adicionar a data de publicação
            df_mapeado['data_publicacao'] = data_publicacao
            
            # Log do DataFrame mapeado antes de salvar
            print("="*50)
            print("DataFrame mapeado antes de salvar:")
            print("Colunas:", df_mapeado.columns.tolist())
            print("="*50)
            
            # Salvar os dados no Supabase
            try:
                num_registros = salvar_no_supabase(df_mapeado, data_publicacao)
                
                if num_registros == 0:
                    return render_template_string(TEMPLATE_CONFIRMACAO, 
                                                session_id=session_id,
                                                arquivo_original=arquivo_original,
                                                mapeamento=mapeamento,
                                                df_preview=df.head(5),
                                                campos_necessarios=CAMPOS_NECESSARIOS,
                                                message=f'Nenhum registro foi importado. Por favor, verifique o mapeamento e tente novamente.',
                                                message_type='error')
                
                # Limpar os dados temporários após o sucesso
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
                
                return render_template_string(HTML_TEMPLATE, 
                                            active_tab='importacao', 
                                            env_vars={
                                                'SUPABASE_URL': '✓ Definido' if os.getenv('SUPABASE_URL') else '✗ Não definido',
                                                'SUPABASE_KEY': '✓ Definido' if os.getenv('SUPABASE_KEY') else '✗ Não definido'
                                            },
                                            message=f'Dados importados com sucesso! {num_registros} registros importados.',
                                            message_type='success',
                                            preview_data=None,
                                            preview_columns=None)
            
            except Exception as e:
                print("="*50)
                print("Erro ao salvar no Supabase:")
                print(str(e))
                traceback.print_exc()
                print("="*50)
                return render_template_string(TEMPLATE_CONFIRMACAO, 
                                            session_id=session_id,
                                            arquivo_original=arquivo_original,
                                            mapeamento=mapeamento,
                                            df_preview=df.head(5),
                                            campos_necessarios=CAMPOS_NECESSARIOS,
                                            message=f'Erro ao processar a importação: {str(e)}',
                                            message_type='error')
        
        except Exception as e:
            print("="*50)
            print("Erro durante o processamento:")
            print(str(e))
            traceback.print_exc()
            print("="*50)
            return render_template_string(TEMPLATE_CONFIRMACAO, 
                                          session_id=session_id,
                                          arquivo_original=arquivo_original,
                                          mapeamento=mapeamento,
                                          df_preview=df.head(5),
                                          campos_necessarios=CAMPOS_NECESSARIOS,
                                          message=f'Erro durante o processamento: {str(e)}',
                                          message_type='error')
    
    # Exibir a página de confirmação
    return render_template_string(TEMPLATE_CONFIRMACAO, 
                                  session_id=session_id,
                                  arquivo_original=arquivo_original,
                                  mapeamento=mapeamento,
                                  df_preview=df.head(5),
                                  campos_necessarios=CAMPOS_NECESSARIOS,
                                  message=None,
                                  message_type=None)

@app.route('/listar_medicamentos')
def listar_medicamentos():
    """
    Rota para listar medicamentos cadastrados no Supabase
    """
    try:
        # Inicializar o cliente Supabase
        supabase = init_supabase()
        
        # Obter contagem total
        response_count = supabase.table('medicamentos').select('count', count='exact').execute()
        total_registros = response_count.count if hasattr(response_count, 'count') else 0
        
        # Listar os registros existentes (limitado a 100)
        response = supabase.table('medicamentos').select('*').order('id', desc=True).limit(100).execute()
        
        if response.data:
            # Formatar os dados para exibição
            dados = []
            for registro in response.data:
                # Filtrar apenas alguns campos relevantes para a visualização
                dados.append({
                    'id': registro.get('id', ''),
                    'substancia': registro.get('substancia', ''),
                    'laboratorio': registro.get('laboratorio', ''),
                    'produto': registro.get('produto', ''),
                    'apresentacao': registro.get('apresentacao', ''),
                    'pf_sem_impostos': registro.get('pf_sem_impostos', ''),
                    'data_publicacao': registro.get('data_publicacao', '')
                })
            
            message = f"{len(dados)} registros encontrados (de um total de {total_registros})"
            message_type = 'success'
        else:
            dados = []
            message = "Nenhum registro encontrado no banco de dados"
            message_type = 'warning'
        
        return render_template_string(
            TEMPLATE_LISTAR_MEDICAMENTOS,
            active_tab='listar',
            env_vars={
                'SUPABASE_URL': '✓ Definido' if os.getenv('SUPABASE_URL') else '✗ Não definido',
                'SUPABASE_KEY': '✓ Definido' if os.getenv('SUPABASE_KEY') else '✗ Não definido'
            },
            message=message,
            message_type=message_type,
            dados=dados
        )
    except Exception as e:
        print(f"Erro ao listar medicamentos: {str(e)}")
        traceback.print_exc()
        
        return render_template_string(
            TEMPLATE_LISTAR_MEDICAMENTOS,
            active_tab='listar',
            env_vars={
                'SUPABASE_URL': '✓ Definido' if os.getenv('SUPABASE_URL') else '✗ Não definido',
                'SUPABASE_KEY': '✓ Definido' if os.getenv('SUPABASE_KEY') else '✗ Não definido'
            },
            message=f"Erro ao listar medicamentos: {str(e)}",
            message_type='error',
            dados=[]
        )

@app.route('/teste_confirmacao')
def teste_confirmacao():
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

@app.route('/teste_html')
def teste_html():
    with open('teste_template.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    return html_content

def open_browser():
    """Abre o navegador após um pequeno atraso"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # Iniciar thread para abrir o navegador
    threading.Thread(target=open_browser).start()
    
    # Iniciar o servidor Flask
    app.run(debug=True, use_reloader=False)
