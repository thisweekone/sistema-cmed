import os
import subprocess
import sys

def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def menu_principal():
    """Exibe o menu principal e processa a escolha do usuário"""
    limpar_tela()
    print("=" * 50)
    print("  SISTEMA DE HISTÓRICO DE PREÇOS CMED")
    print("=" * 50)
    print("\nEscolha uma opção:")
    print("1. Verificar conexão com Supabase")
    print("2. Ver instruções para criar tabelas")
    print("3. Testar processamento de arquivo CMED")
    print("4. Importar dados para Supabase")
    print("5. Iniciar aplicação Streamlit")
    print("0. Sair")
    
    try:
        opcao = int(input("\nOpção: "))
        return opcao
    except ValueError:
        return -1

def executar_script(script, args=None):
    """Executa um script Python"""
    comando = [sys.executable, script]
    if args:
        comando.extend(args)
    
    try:
        subprocess.run(comando)
    except Exception as e:
        print(f"Erro ao executar {script}: {e}")
    
    input("\nPressione Enter para continuar...")

def main():
    """Função principal"""
    while True:
        opcao = menu_principal()
        
        if opcao == 0:
            print("Saindo...")
            break
        elif opcao == 1:
            executar_script("verificar_conexao.py")
        elif opcao == 2:
            executar_script("setup_database.py")
        elif opcao == 3:
            executar_script("testar_importacao.py")
        elif opcao == 4:
            executar_script("importar_dados.py")
        elif opcao == 5:
            print("\nIniciando aplicação Streamlit...")
            print("Pressione Ctrl+C para encerrar a aplicação quando terminar.")
            try:
                subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])
            except KeyboardInterrupt:
                print("\nAplicação encerrada.")
            input("\nPressione Enter para continuar...")
        else:
            print("\nOpção inválida. Tente novamente.")
            input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
