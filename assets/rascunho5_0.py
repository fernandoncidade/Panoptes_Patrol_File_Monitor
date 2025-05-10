# filepath: c:\Users\ferna\WORK\Projetos_Python\File-Folder-Manager\rascunho_File_Manager\teste1.py
import subprocess
import os
import sys
import time
import shutil

def find_signtool():
    """Procura o signtool em locais conhecidos."""
    # Caminho fornecido pelo usuário
    user_path = r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"
    
    # Lista de caminhos conhecidos do SDK do Windows
    possible_paths = [
        user_path,
        r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe",
        r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22000.0\x64\signtool.exe",
        r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe",
        r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.18362.0\x64\signtool.exe",
        # Verifica se está no PATH
        shutil.which("signtool")
    ]
    
    # Tenta encontrar o primeiro caminho válido
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    
    return None

def verify_signature(file_path):
    """Verifica a assinatura digital de um arquivo executável."""
    # Verificar se o arquivo existe
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False
    
    # Encontrar o signtool
    signtool_path = find_signtool()
    if not signtool_path:
        print("❌ ERRO: SignTool não encontrado.")
        print("Por favor, verifique se o Windows SDK está instalado corretamente.")
        print("Você pode baixar o SDK em: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/")
        return False
    
    print(f"✅ SignTool encontrado: {signtool_path}")
    
    try:
        print(f"🔍 Verificando assinatura de: {file_path}")
        # Usando SignTool com caminho absoluto
        result = subprocess.run(
            [signtool_path, "verify", "/pa", "/v", file_path],
            capture_output=True,
            text=True
        )
        
        if "Successfully verified" in result.stdout:
            print("✅ Arquivo assinado corretamente")
            print(result.stdout)
            return True
        else:
            print("❌ Problema na assinatura do arquivo")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar assinatura: {e}")
        return False

def main():
    # Os possíveis caminhos para o instalador e o executável
    possible_paths = [
        # Caminho do executável
        r"C:\Users\ferna\WORK\Projetos_Python\File-Folder-Manager\rascunho_File_Manager\dist\Panoptes_Patrol\Panoptes_Patrol.exe",
        # Caminho do instalador
        r"C:\Users\ferna\WORK\Projetos_Python\File-Folder-Manager\rascunho_File_Manager\dist\Panoptes_Patrol_Windows_x64_setup_v001.exe"
    ]
    
    print("=== VERIFICAÇÃO DE ASSINATURAS DIGITAIS ===")
    
    found = False
    for path in possible_paths:
        if os.path.exists(path):
            found = True
            print(f"\nVerificando arquivo: {path}")
            verify_signature(path)
    
    if not found:
        print("\n❌ NENHUM ARQUIVO ENCONTRADO!")
        print("Arquivos procurados:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\nDigite o caminho completo do arquivo para verificar:")
        custom_path = input("> ").strip()
        if custom_path:
            verify_signature(custom_path)
    
if __name__ == "__main__":
    main()
    