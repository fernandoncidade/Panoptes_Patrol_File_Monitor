import os
from .gmet_21_GetFormataTamanho import get_formata_tamanho

def extrair_metadados_arquivo(caminho, loc):
    metadados = {}
    ext = os.path.splitext(caminho)[1].lower()

    try:
        if ext == '.zip':
            try:
                import zipfile
                with zipfile.ZipFile(caminho, 'r') as zip_ref:
                    arquivos = zip_ref.namelist()
                    qtd_arquivos = len(arquivos)

                    tamanho_total = sum(info.file_size for info in zip_ref.infolist())
                    tamanho_compactado = os.path.getsize(caminho)

                    if tamanho_total > 0:
                        taxa_compressao = (1 - tamanho_compactado / tamanho_total) * 100

                    else:
                        taxa_compressao = 0

                    metadados['arquivos'] = qtd_arquivos
                    metadados['tamanho_descompactado'] = get_formata_tamanho(tamanho_total)
                    metadados['taxa_compressao'] = f"{taxa_compressao:.1f}%"

                    if arquivos:
                        arquivos_top = sorted([a for a in arquivos if '/' not in a])[:5]
                        if arquivos_top:
                            metadados['conteudo'] = ", ".join(arquivos_top)
                            if len(arquivos) > 5:
                                metadados['conteudo'] += f" {loc.get_text("and_others")} {len(arquivos)-5}"

            except Exception as e:
                print(f"Erro ao extrair metadados do ZIP {caminho}: {e}")

        elif ext == '.rar':
            try:
                import rarfile
                with rarfile.RarFile(caminho) as rar:
                    arquivos = rar.namelist()
                    qtd_arquivos = len(arquivos)

                    tamanho_total = sum(f.file_size for f in rar.infolist())
                    tamanho_compactado = os.path.getsize(caminho)

                    if tamanho_total > 0:
                        taxa_compressao = (1 - tamanho_compactado / tamanho_total) * 100

                    else:
                        taxa_compressao = 0

                    metadados['arquivos'] = qtd_arquivos
                    metadados['tamanho_descompactado'] = get_formata_tamanho(tamanho_total)
                    metadados['taxa_compressao'] = f"{taxa_compressao:.1f}%"

                    if arquivos:
                        arquivos_top = sorted([a for a in arquivos if '/' not in a])[:5]
                        if arquivos_top:
                            metadados['conteudo'] = ", ".join(arquivos_top)
                            if len(arquivos) > 5:
                                metadados['conteudo'] += f" {loc.get_text("and_others")} {len(arquivos)-5}"

            except Exception as e:
                print(f"Erro ao extrair metadados do RAR {caminho}: {e}")

        elif ext == '.7z':
            try:
                import py7zr
                with py7zr.SevenZipFile(caminho, mode='r') as z:
                    arquivos = z.getnames()
                    qtd_arquivos = len(arquivos)

                    arquivos_info = z.list()
                    tamanho_total = sum(info.uncompressed for info in arquivos_info)
                    tamanho_compactado = os.path.getsize(caminho)

                    if tamanho_total > 0:
                        taxa_compressao = (1 - tamanho_compactado / tamanho_total) * 100

                    else:
                        taxa_compressao = 0

                    metadados['arquivos'] = qtd_arquivos
                    metadados['tamanho_descompactado'] = get_formata_tamanho(tamanho_total)
                    metadados['taxa_compressao'] = f"{taxa_compressao:.1f}%"

                    if arquivos:
                        arquivos_top = sorted([a for a in arquivos if '/' not in a])[:5]
                        if arquivos_top:
                            metadados['conteudo'] = ", ".join(arquivos_top)
                            if len(arquivos) > 5:
                                metadados['conteudo'] += f" {loc.get_text('and_others')} {len(arquivos)-5}"

            except Exception as e:
                print(f"Erro ao extrair metadados do 7Z {caminho}: {e}")

    except Exception as e:
        print(f"Erro geral ao extrair metadados do arquivo compactado {caminho}: {e}")

    return metadados
