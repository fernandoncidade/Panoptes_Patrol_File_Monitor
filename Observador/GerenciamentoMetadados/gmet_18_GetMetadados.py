import os
from datetime import datetime
from .gmet_02_ExtrairMetadadosCodigoFonte import extrair_metadados_codigo_fonte
from .gmet_03_ExtrairMetadadosImagem import extrair_metadados_imagem
from .gmet_04_ExtrairMetadadosAudio import extrair_metadados_audio
from .gmet_05_ExtrairMetadadosVideo import extrair_metadados_video
from .gmet_06_ExtrairMetadadosDocumento import extrair_metadados_documento
from .gmet_07_ExtrairMetadadosPlanilha import extrair_metadados_planilha
from .gmet_08_ExtrairMetadadosApresentacao import extrair_metadados_apresentacao
from .gmet_09_ExtrairMetadadosBancoDados import extrair_metadados_banco_dados
from .gmet_10_ExtrairMetadadosExecutavel import extrair_metadados_executavel
from .gmet_11_ExtrairMetadadosTemporario import extrair_metadados_temporario
from .gmet_12_ExtrairMetadadosArquivo import extrair_metadados_arquivo
from .gmet_13_ExtrairMetadadosBackup import extrair_metadados_backup
from .gmet_14_ExtrairMetadadosLog import extrair_metadados_log
from .gmet_15_ExtrairMetadadosConfig import extrair_metadados_config
from .gmet_17_ExtrairMetadadosDadosEstruturados import extrair_metadados_dados_estruturados
from .gmet_19_GetTipoArquivo import identificar_tipo_arquivo
from .gmet_20_GetTamanhoDiretorioArquivo import get_tamanho_diretorio_arquivo
from .gmet_22_GetAtributosArquivo import get_atributos_arquivo
from .gmet_23_GetAutorArquivo import get_autor_arquivo
from .gmet_27_GetProtecaoArquivo import get_protecao_arquivo

def extrair_metadados_completos(item, loc=None, contexto=None):
    try:
        caminho = item.get("dir_atual") or item.get("dir_anterior")
        if not caminho or not os.path.exists(caminho):
            return {}

        stats = os.stat(caminho)

        metadados = {
            "tamanho": get_tamanho_diretorio_arquivo(contexto, item, loc) if contexto and loc else str(stats.st_size),
            "data_acesso": datetime.fromtimestamp(stats.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
            "data_modificacao": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "data_criacao": datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            "atributos": get_atributos_arquivo(item, loc) if loc else "",
            "autor": get_autor_arquivo(item, loc) if loc else "",
            "protegido": get_protecao_arquivo(item, loc) if loc else ""
        }

        if loc is None:
            return metadados

        tipo_arquivo = identificar_tipo_arquivo(caminho, loc)

        ext = os.path.splitext(caminho)[1].lower()
        if ext == '.dat':
            metadados.update(extrair_metadados_dados_estruturados(caminho, loc))

        elif tipo_arquivo == loc.get_text("file_video"):
            metadados.update(extrair_metadados_video(caminho))

        elif tipo_arquivo == loc.get_text("file_image"):
            metadados.update(extrair_metadados_imagem(caminho))

        elif tipo_arquivo == loc.get_text("file_audio"):
            metadados.update(extrair_metadados_audio(caminho))

        elif tipo_arquivo == loc.get_text("file_source_code"):
            metadados.update(extrair_metadados_codigo_fonte(caminho))

        elif tipo_arquivo == loc.get_text("file_document"):
            metadados.update(extrair_metadados_documento(caminho))

        elif tipo_arquivo == loc.get_text("file_spreadsheet"):
            metadados.update(extrair_metadados_planilha(caminho))

        elif tipo_arquivo == loc.get_text("file_presentation"):
            metadados.update(extrair_metadados_apresentacao(caminho))

        elif tipo_arquivo == loc.get_text("file_database"):
            metadados.update(extrair_metadados_banco_dados(caminho))

        elif tipo_arquivo == loc.get_text("file_executable"):
            metadados.update(extrair_metadados_executavel(caminho))

        elif tipo_arquivo == loc.get_text("file_temp"):
            metadados.update(extrair_metadados_temporario(caminho))

        elif tipo_arquivo == loc.get_text("file_archive"):
            metadados.update(extrair_metadados_arquivo(caminho))

        elif tipo_arquivo == loc.get_text("file_backup"):
            metadados.update(extrair_metadados_backup(caminho, loc))

        elif tipo_arquivo == loc.get_text("file_log"):
            metadados.update(extrair_metadados_log(caminho))

        elif tipo_arquivo == loc.get_text("file_config"):
            metadados.update(extrair_metadados_config(caminho))

        return metadados

    except Exception as e:
        print(f"Erro ao obter metadados completos: {e}")
        return {}

get_metadados = extrair_metadados_completos
