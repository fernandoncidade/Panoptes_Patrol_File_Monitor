import os
from .gmet_16_ExtrairMetadadosOlefile import extrair_metadados_olefile

def extrair_metadados_apresentacao(caminho, loc):
    metadados = {}
    ext = os.path.splitext(caminho)[1].lower()

    try:
        if ext in ['.pptx', '.ppt']:
            try:
                if ext == '.pptx':
                    from pptx import Presentation
                    prs = Presentation(caminho)

                    slides = len(prs.slides)
                    metadados['slides'] = slides

                    if prs.core_properties:
                        props = prs.core_properties
                        if props.author:
                            metadados['autor'] = props.author

                        if props.title:
                            metadados['titulo'] = props.title

                        if props.created:
                            metadados['data_criacao_doc'] = str(props.created)

                        if props.modified:
                            metadados['data_mod_doc'] = str(props.modified)

                        if hasattr(props, 'content_status') and props.content_status:
                            if "protected" in str(props.content_status).lower():
                                metadados['protegido'] = loc.get_text("yes")

                elif ext == '.ppt':
                    try:
                        ppt_metadados = extrair_metadados_olefile(caminho)
                        if ppt_metadados and 'slides' in ppt_metadados:
                            metadados.update(ppt_metadados)

                        else:
                            raise Exception("Falha ao obter metadados via Tika")

                    except Exception as e:
                        print(f"Usando fallback para olefile: {e}")

                        import olefile
                        if olefile.isOleFile(caminho):
                            with olefile.OleFile(caminho) as ole:
                                tamanho = os.path.getsize(caminho)
                                slides_estimados = max(1, tamanho // 100000)

                                if ole.exists('\x05DocumentSummaryInformation'):
                                    info = ole.getproperties('\x05DocumentSummaryInformation')

                                    if 19 in info:
                                        metadados['protegido'] = loc.get_text("yes")

                                if ole.exists('\x05SummaryInformation'):
                                    info = ole.getproperties('\x05SummaryInformation')

                                    if 4 in info:
                                        metadados['autor'] = info[4]

                                    if 2 in info:
                                        metadados['titulo'] = info[2]

            except Exception as e:
                print(f"Erro ao extrair metadados da apresentação {caminho}: {e}")

    except Exception as e:
        print(f"Erro geral ao extrair metadados da apresentação {caminho}: {e}")

    return metadados
