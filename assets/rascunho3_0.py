import subprocess
import os
import sys

def assinar_msix(caminho_msix, caminho_pfx, senha, timestamp_url=None):
    """Assina um pacote MSIX usando SignTool do Windows SDK."""
    
    # Encontra o caminho do SignTool
    sdk_paths = [
        r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64",
        r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64",
        r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64"
    ]
    
    signtool_path = None
    for path in sdk_paths:
        if os.path.exists(os.path.join(path, "signtool.exe")):
            signtool_path = os.path.join(path, "signtool.exe")
            break
    
    if not signtool_path:
        print("Erro: SignTool não encontrado. Verifique se o Windows SDK está instalado.")
        return False
    
    # Prepara o comando base
    cmd = [signtool_path, "sign", "/fd", "SHA256", "/f", caminho_pfx, "/p", senha]
    
    # Adiciona timestamp se fornecido
    if timestamp_url:
        cmd.extend(["/tr", timestamp_url, "/td", "SHA256"])
    
    # Adiciona o caminho do MSIX
    cmd.append(caminho_msix)
    
    try:
        # Executa o comando
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Verifica o resultado
        if result.returncode == 0:
            print("Assinatura concluída com sucesso!")
            return True
        else:
            print(f"Erro na assinatura: {result.stderr}")
            return False
    except Exception as e:
        print(f"Erro ao executar SignTool: {str(e)}")
        return False

if __name__ == "__main__":
    caminho_msix = r"C:\Users\ferna\WORK\Projetos_Python\File-Folder-Manager\Panoptes_Patrol_File_Monitor\Panoptes_Patrol.msix"
    caminho_pfx = r"C:\Users\ferna\WORK\Projetos_Python\File-Folder-Manager\Panoptes_Patrol_File_Monitor\test_cert.pfx"
    senha = "Senha123"
    timestamp_url = "http://timestamp.digicert.com"
    
    sucesso = assinar_msix(caminho_msix, caminho_pfx, senha, timestamp_url)
    sys.exit(0 if sucesso else 1)
