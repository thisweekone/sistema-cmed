import os
import subprocess
import sys
import time

def main():
    """
    Script para executar o aplicativo Streamlit e abrir automaticamente o navegador.
    """
    print("=== Iniciando Aplicativo Streamlit ===")
    
    # Verificar se o Streamlit está instalado
    try:
        import streamlit
        print(f"✅ Streamlit instalado (versão {streamlit.__version__})")
    except ImportError:
        print("❌ Streamlit não está instalado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], check=True)
        print("✅ Streamlit instalado com sucesso!")
    
    # Verificar arquivo .env
    if os.path.exists(".env"):
        print("✅ Arquivo .env encontrado")
    else:
        print("❌ Arquivo .env não encontrado. Criando arquivo de exemplo...")
        with open(".env", "w") as f:
            f.write("SUPABASE_URL=sua_url_do_supabase\n")
            f.write("SUPABASE_KEY=sua_chave_do_supabase\n")
        print("✅ Arquivo .env de exemplo criado. Por favor, edite-o com suas credenciais reais.")
        return
    
    # Verificar arquivo app.py
    if os.path.exists("app.py"):
        print("✅ Arquivo app.py encontrado")
    else:
        print("❌ Arquivo app.py não encontrado")
        return
    
    # Iniciar o servidor Streamlit
    print("\n=== Iniciando Servidor Streamlit ===")
    print("O aplicativo será aberto no navegador em alguns segundos...")
    print("Para interromper o servidor, pressione Ctrl+C neste terminal")
    print("Endereço do aplicativo: http://localhost:8501")
    print("===================================\n")
    
    # Executar o comando streamlit run
    try:
        # Usar subprocess.Popen para não bloquear este script
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app_simples.py"], 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Esperar um pouco para o servidor iniciar
        time.sleep(3)
        
        # Abrir o navegador automaticamente
        import webbrowser
        webbrowser.open("http://localhost:8501")
        
        # Manter o script rodando e mostrar a saída do processo
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())
            
            # Verificar se o processo ainda está rodando
            if process.poll() is not None:
                break
            
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nInterrompendo o servidor Streamlit...")
        process.terminate()
    
    print("Servidor Streamlit encerrado.")

if __name__ == "__main__":
    main()
