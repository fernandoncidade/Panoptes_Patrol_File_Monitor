import os

def extrair_metadados_olefile(caminho, loc):
    metadados = {}
    ext = os.path.splitext(caminho)[1].lower()

    try:
        if ext == '.doc':
            import olefile
            if olefile.isOleFile(caminho):
                with olefile.OleFile(caminho) as ole:
                    if ole.exists('\x05SummaryInformation'):
                        info = ole.getproperties('\x05SummaryInformation')
                        if 4 in info:
                            metadados['autor'] = info[4]

                        if 19 in info and info[19]:
                            metadados['protegido'] = loc.get_text("yes")

                    tamanho = os.path.getsize(caminho)
                    paginas_estimadas = max(1, tamanho // 20000)
                    metadados['paginas'] = paginas_estimadas
                    metadados['dimensoes'] = f"{paginas_estimadas} {loc.get_text('pages_estimated')}"

        elif ext == '.ppt':
            import olefile
            if olefile.isOleFile(caminho):
                with olefile.OleFile(caminho) as ole:
                    if ole.exists('\x05SummaryInformation'):
                        info = ole.getproperties('\x05SummaryInformation')
                        if 4 in info:
                            metadados['autor'] = info[4]

                tamanho = os.path.getsize(caminho)
                slides_estimados = max(1, tamanho // 100000)
                metadados['slides'] = slides_estimados
                metadados['dimensoes'] = f"{slides_estimados} {loc.get_text('slides_estimated')}"

    except Exception as e:
        print(f"Erro ao extrair metadados sem Tika: {e}")
        tamanho = os.path.getsize(caminho)
        if ext == '.doc':
            paginas_estimadas = max(1, tamanho // 20000)
            metadados['dimensoes'] = f"{paginas_estimadas} {loc.get_text('pages_estimated')}"

        elif ext == '.ppt':
            slides_estimados = max(1, tamanho // 100000)
            metadados['dimensoes'] = f"{slides_estimados} {loc.get_text('slides_estimated')}"

    return metadados
