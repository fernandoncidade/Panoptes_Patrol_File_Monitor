import os
import time

def extrair_metadados_temporario(caminho, loc):
    metadados = {}

    try:
        nome_arquivo = os.path.basename(caminho)
        aplicativos_conhecidos = {
            "~$": "Microsoft Office",
            ".crdownload": "Google Chrome",
            ".part": "Firefox/Navegador",
            ".download": "Navegador",
            ".tmp": "Aplicação Windows",
            ".swp": "Editor Vi/Vim",
            "._": "macOS",
            ".partial": "Download parcial",
            ".temp": "Aplicação temporária",
            "thumb": "Miniaturas",
            "cache": "Arquivo de cache"
        }

        for prefixo, aplicativo in aplicativos_conhecidos.items():
            if prefixo in nome_arquivo:
                metadados['aplicativo_origem'] = aplicativo
                break

        tempo_atual = time.time()
        stats = os.stat(caminho)
        idade_em_horas = (tempo_atual - stats.st_mtime) / 3600

        if idade_em_horas < 1:
            metadados['idade'] = f"{int(idade_em_horas * 60)} {loc.get_text('minutes')}"

        elif idade_em_horas < 24:
            metadados['idade'] = f"{int(idade_em_horas)} {loc.get_text('hours')}"

        else:
            metadados['idade'] = f"{int(idade_em_horas / 24)} {loc.get_text('days')}"

        diretorio = os.path.dirname(caminho)
        nome_base = nome_arquivo

        for prefixo in ["~$", "._", ".#"]:
            if nome_base.startswith(prefixo):
                nome_base = nome_base[len(prefixo):]

        for sufixo in [".tmp", ".temp", ".~", ".swp", ".swo", ".$$", ".old", ".part", 
                       ".cache", ".crdownload", ".download", ".partial", ".lock", "thumb"]:
            if nome_base.endswith(sufixo):
                nome_base = nome_base[:-len(sufixo)]

        arquivos_similares = []
        if os.path.exists(diretorio):
            for arquivo in os.listdir(diretorio):
                if nome_base in arquivo and arquivo != nome_arquivo:
                    arquivos_similares.append(arquivo)

        if arquivos_similares:
            metadados['arquivos_relacionados'] = ", ".join(arquivos_similares[:3])
            if len(arquivos_similares) > 3:
                metadados['arquivos_relacionados'] += f" {loc.get_text("and_others")} {len(arquivos_similares)-3}"

    except Exception as e:
        print(f"Erro ao extrair metadados do arquivo temporário {caminho}: {e}")

    return metadados
