import os
from .gmet_16_ExtrairMetadadosOlefile import extrair_metadados_olefile

def extrair_metadados_documento(caminho, loc):
    metadados = {}
    ext = os.path.splitext(caminho)[1].lower()

    try:
        if ext == '.pdf':
            try:
                from PyPDF2 import PdfReader
                reader = PdfReader(caminho)
                paginas = len(reader.pages)
                metadados['dimensoes'] = f"{paginas} {loc.get_text("pages")}"

                info = reader.metadata
                if info:
                    if info.title:
                        metadados['titulo'] = info.title

                    if info.author:
                        metadados['autor'] = info.author

                    if info.creator:
                        metadados['criador'] = info.creator

                    if info.producer:
                        metadados['produtor'] = info.producer

                    if info.creation_date:
                        metadados['data_criacao_doc'] = str(info.creation_date)

                    if info.modification_date:
                        metadados['data_mod_doc'] = str(info.modification_date)

            except Exception as e:
                print(f"Erro ao extrair metadados do PDF {caminho}: {e}")

        elif ext in ['.docx', '.doc']:
            try:
                if ext == '.docx':
                    from docx import Document
                    doc = Document(caminho)
                    paragrafos = len(doc.paragraphs)
                    paginas_estimadas = paragrafos // 40
                    metadados['paginas_estimadas'] = paginas_estimadas
                    metadados['parágrafos'] = paragrafos
                    metadados['dimensoes'] = f"{paginas_estimadas} {loc.get_text("pages_estimated")}, {paragrafos} {loc.get_text("paragraphs")}"

                    try:
                        props = doc.core_properties
                        if props:
                            if props.title:
                                metadados['titulo'] = props.title

                            if props.author:
                                metadados['autor'] = props.author

                            if props.created:
                                metadados['data_criacao_doc'] = str(props.created)

                            if props.modified:
                                metadados['data_mod_doc'] = str(props.modified)

                            if props.revision:
                                metadados['revisão'] = props.revision
                    except Exception as prop_err:
                        if "document is encrypted" in str(prop_err).lower():
                            metadados['protegido'] = loc.get_text("yes") + " (senha)"
                        else:
                            print(f"Erro ao extrair propriedades de DOCX: {prop_err}")

                elif ext == '.doc':
                    try:
                        doc_metadados = extrair_metadados_olefile(caminho)
                        if doc_metadados and 'dimensoes' in doc_metadados:
                            metadados.update(doc_metadados)

                        else:
                            raise Exception("Falha ao obter metadados via Tika")

                    except Exception as e:
                        print(f"Usando fallback para olefile: {e}")

                        import olefile
                        if olefile.isOleFile(caminho):
                            with olefile.OleFile(caminho) as ole:
                                tamanho = os.path.getsize(caminho)
                                paginas_estimadas = max(1, tamanho // 20000)
                                metadados['dimensoes'] = f"{paginas_estimadas} {loc.get_text("pages_estimated")}"

                                if ole.exists('\x05SummaryInformation'):
                                    info = ole.getproperties('\x05SummaryInformation')
                                    if 4 in info:
                                        metadados['autor'] = info[4]

                                    if 2 in info:
                                        metadados['titulo'] = info[2]

                                    if 8 in info:
                                        metadados['última_mod'] = info[8]

                                    if 12 in info:
                                        metadados['criação'] = info[12]

                                    if 19 in info:
                                        metadados['protegido'] = loc.get_text("yes") + f" ({info[19]})"

            except Exception as e:
                print(f"Erro ao extrair metadados do documento {caminho}: {e}")

        elif ext == '.txt':
            try:
                linhas = 0
                palavras = 0
                caracteres = 0

                with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
                    for linha in f:
                        linhas += 1
                        palavras += len(linha.split())
                        caracteres += len(linha)

                metadados['linhas'] = linhas
                metadados['palavras'] = palavras
                metadados['caracteres'] = caracteres
                metadados['dimensoes'] = f"{linhas} {loc.get_text("lines")}, {palavras} {loc.get_text("words")}"

            except Exception as e:
                print(f"Erro ao extrair metadados do TXT {caminho}: {e}")

    except Exception as e:
        print(f"Erro geral ao extrair metadados do documento {caminho}: {e}")

    return metadados
