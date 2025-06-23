import os
import chardet
from .gmet_21_GetFormataTamanho import get_formata_tamanho

def extrair_metadados_dados_estruturados(caminho, loc):
    metadados = {}
    
    try:
        tamanho_arquivo = os.path.getsize(caminho)
        metadados['tamanho'] = get_formata_tamanho(tamanho_arquivo)

        eh_binario = False
        com_byte_count = 0

        with open(caminho, 'rb') as f:
            sample = f.read(4096)

            for byte in sample:
                if byte == 0 or byte > 127:
                    com_byte_count += 1

            eh_binario = com_byte_count > len(sample) * 0.1

            if eh_binario:
                metadados['formato'] = "Arquivo de dados binário"

                tamanhos_comuns = [4, 8, 16, 32, 64, 128, 256, 512, 1024]
                for tamanho in tamanhos_comuns:
                    if tamanho_arquivo % tamanho == 0 and tamanho_arquivo > 0:
                        registros_estimados = tamanho_arquivo // tamanho
                        metadados['registros'] = str(registros_estimados)
                        metadados['bytes_por_registro'] = str(tamanho)
                        break

                if 'registros' not in metadados:
                    metadados['binario'] = f"{tamanho_arquivo} {loc.get_text('bytes')}"

            else:
                encoding_result = chardet.detect(sample)
                encoding = encoding_result['encoding'] if encoding_result['encoding'] else 'utf-8'

                f.seek(0)
                conteudo = f.read(min(1024*1024, tamanho_arquivo))

                try:
                    texto = conteudo.decode(encoding, errors='replace')
                    linhas = texto.count('\n') + (0 if texto.endswith('\n') else 1)

                    linhas_texto = texto.split('\n', 10)[:10]
                    if linhas_texto:
                        primeira_linha = linhas_texto[0]

                        delimitadores = {
                            ',': primeira_linha.count(','),
                            '\t': primeira_linha.count('\t'),
                            '|': primeira_linha.count('|'),
                            ';': primeira_linha.count(';')
                        }

                        delimitador = max(delimitadores.items(), key=lambda x: x[1])[0]
                        colunas = delimitadores[delimitador] + 1 if delimitadores[delimitador] > 0 else 0

                        if colunas > 1:
                            metadados['formato'] = f"Arquivo de dados delimitado ({delimitador})"
                            metadados['registros'] = str(linhas)
                            metadados['colunas'] = str(colunas)

                        else:
                            metadados['formato'] = "Arquivo de dados de texto"
                            metadados['linhas'] = str(linhas)

                    else:
                        metadados['formato'] = "Arquivo de dados de texto"
                        metadados['binario'] = f"{tamanho_arquivo} {loc.get_text('bytes')}"

                except:
                    metadados['formato'] = "Arquivo de dados"
                    metadados['binario'] = f"{tamanho_arquivo} {loc.get_text('bytes')}"

    except Exception as e:
        print(f"Erro ao extrair metadados de arquivo de dados {caminho}: {e}")
        metadados['binario'] = f"{tamanho_arquivo} {loc.get_text('bytes')}"

    return metadados
