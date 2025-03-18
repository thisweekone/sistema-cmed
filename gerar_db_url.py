import os
from dotenv import load_dotenv
import base64
import json

def decode_jwt(jwt):
    """Decodifica um token JWT e retorna o payload"""
    # Pegar a parte do payload (segunda parte do token)
    payload_b64 = jwt.split('.')[1]
    # Adicionar padding se necessário
    padding = 4 - (len(payload_b64) % 4)
    if padding != 4:
        payload_b64 += '=' * padding
    # Decodificar
    payload = base64.b64decode(payload_b64)
    return json.loads(payload)

def gerar_db_url():
    """Gera a URL do banco de dados a partir das credenciais do Supabase"""
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Obter credenciais do Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos no arquivo .env")
    
    try:
        # Decodificar o token JWT para obter as credenciais do banco
        jwt_payload = decode_jwt(supabase_key)
        
        # Extrair informações do host do Supabase URL
        # Formato: https://[project_id].supabase.co
        project_id = supabase_url.split('//')[1].split('.')[0]
        
        # Construir a URL do banco de dados
        db_url = f"postgresql://postgres:{jwt_payload['db_pass']}@db.{project_id}.supabase.co:5432/postgres"
        
        # Atualizar o arquivo .env
        env_path = '.env'
        env_content = []
        
        # Ler o arquivo .env existente
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                env_content = f.readlines()
        
        # Procurar e atualizar/adicionar SUPABASE_DB_URL
        db_url_line = f'SUPABASE_DB_URL="{db_url}"\n'
        db_url_found = False
        
        for i, line in enumerate(env_content):
            if line.startswith('SUPABASE_DB_URL='):
                env_content[i] = db_url_line
                db_url_found = True
                break
        
        if not db_url_found:
            env_content.append(db_url_line)
        
        # Salvar o arquivo .env atualizado
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(env_content)
        
        print("URL do banco de dados gerada e salva no arquivo .env")
        return db_url
        
    except Exception as e:
        print(f"Erro ao gerar URL do banco de dados: {str(e)}")
        raise

if __name__ == "__main__":
    gerar_db_url()
