import os
import time
from .gmet_21_GetFormataTamanho import formata_tamanho

def extrair_metadados_backup(caminho, loc):
    metadados = {}
    nome_arquivo = os.path.basename(caminho)

    try:
        aplicativos_backup = {
            "backup": "Backup genérico",
            "bkp": "Backup genérico", 
            "bak": "Backup genérico",
            ".old": "Versão antiga",
            "save": "Arquivo salvo",
            "restore": "Ponto de restauração",
            "autorecovery": "Recuperação automática",
            "autosave": "Salvamento automático",
            "snapshot": "Captura de estado",
            ".gbk": "Backup Git",
            "timemachine": "Time Machine (Mac)"
        }

        for indicador, tipo in aplicativos_backup.items():
            if indicador in nome_arquivo.lower():
                metadados['tipo_backup'] = tipo
                break

        else:
            metadados['tipo_backup'] = "Backup não identificado"

        nome_sem_extensoes = nome_arquivo
        for ext in ['.bak', '.bkp', '.backup', '.old', '.orig', '.save', '.sav', '.auto']:
            if nome_sem_extensoes.lower().endswith(ext):
                nome_sem_extensoes = nome_sem_extensoes[:-len(ext)]

        import re
        padroes_data = [
            r'(\d{4}[-_]?\d{2}[-_]?\d{2})',  # YYYY-MM-DD
            r'(\d{2}[-_]?\d{2}[-_]?\d{4})',  # DD-MM-YYYY
            r'(\d{2}[-_]?\d{2}[-_]?\d{2})'   # DD-MM-YY
        ]

        for padrao in padroes_data:
            match = re.search(padrao, nome_arquivo)
            if match:
                data_backup = match.group(1)
                metadados['data_no_nome'] = data_backup
                break

        diretorio = os.path.dirname(caminho)
        arquivos_relacionados = []

        if os.path.exists(diretorio):
            for arquivo in os.listdir(diretorio):
                if nome_sem_extensoes in arquivo and arquivo != nome_arquivo:
                    caminho_completo = os.path.join(diretorio, arquivo)
                    if os.path.isfile(caminho_completo):
                        arquivos_relacionados.append((arquivo, os.path.getmtime(caminho_completo)))

        if arquivos_relacionados:
            arquivos_relacionados.sort(key=lambda x: x[1], reverse=True)
            arquivo_original, data_mod = arquivos_relacionados[0]

            tempo_backup = os.path.getmtime(caminho)
            diferenca_segundos = abs(tempo_backup - data_mod)

            if diferenca_segundos < 3600:
                metadados['diferenca_original'] = f"{int(diferenca_segundos/60)} {loc.get_text('minutes')}"

            elif diferenca_segundos < 86400:
                metadados['diferenca_original'] = f"{int(diferenca_segundos/3600)} {loc.get_text('hours')}"

            else:
                metadados['diferenca_original'] = f"{int(diferenca_segundos/86400)} {loc.get_text('days')}"

            metadados['arquivo_original'] = arquivo_original

        try:
            if eh_arquivo_texto(caminho):
                num_linhas = contar_linhas(caminho)
                metadados['linhas'] = str(num_linhas)

            else:
                tamanho = os.path.getsize(caminho)
                metadados['binario'] = formata_tamanho(tamanho)

        except Exception as e:
            print(f"Erro ao contar linhas do arquivo de backup {caminho}: {e}")

            try:
                tamanho = os.path.getsize(caminho)
                metadados['tamanho'] = formata_tamanho(tamanho)

            except:
                pass

    except Exception as e:
        print(f"Erro ao extrair metadados do backup {caminho}: {e}")

    return metadados

def eh_arquivo_texto(caminho):
    try:
        with open(caminho, 'rb') as f:
            sample = f.read(1024)

        texto_invalido = sum(1 for b in sample if b < 9 or (b > 13 and b < 32 and b != 27))
        return texto_invalido / len(sample) < 0.3 if sample else False

    except Exception:
        return False

def contar_linhas(caminho):
    try:
        with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)

    except Exception:
        try:
            with open(caminho, 'r', encoding='latin-1', errors='ignore') as f:
                return sum(1 for _ in f)

        except Exception as e:
            print(f"Erro ao contar linhas: {e}")
            return 0
