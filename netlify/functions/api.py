import os
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs

# Esta é uma implementação simples para mostrar a página principal
# Para uma aplicação real, você precisaria adaptar sua lógica Flask para AWS Lambda/Netlify Functions
class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html_content = """
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Sistema CMED - Hospedado no Netlify</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container py-4">
                <h1 class="mb-4">Sistema de Importação CMED</h1>
                <div class="alert alert-info">
                    <p>Esta é uma versão demonstrativa do Sistema CMED hospedada no Netlify.</p>
                    <p>Para funcionalidade completa, execute a aplicação Flask localmente:</p>
                    <code>python app_flask.py</code>
                </div>
                
                <div class="card mb-4">
                    <div class="card-header">Informações do Projeto</div>
                    <div class="card-body">
                        <p>O Sistema CMED permite a importação e consulta de dados da tabela de medicamentos 
                        da Câmara de Regulação do Mercado de Medicamentos (CMED).</p>
                        
                        <h5>Principais Funcionalidades:</h5>
                        <ul>
                            <li>Importação de arquivos CSV, XLS e XLSX</li>
                            <li>Mapeamento inteligente de colunas</li>
                            <li>Validação e processamento seguro dos dados</li>
                            <li>Listagem dos medicamentos cadastrados</li>
                        </ul>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-header">Links Úteis</div>
                    <div class="card-body">
                        <ul>
                            <li><a href="https://github.com/thisweekone/sistema-cmed" target="_blank">Repositório no GitHub</a></li>
                            <li><a href="https://www.gov.br/anvisa/pt-br/assuntos/medicamentos/cmed" target="_blank">Portal CMED/ANVISA</a></li>
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(html_content.encode("utf-8"))
        return
