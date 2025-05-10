import os
from .gmet_18_GetMetadados import get_metadados
from .gmet_13_ExtrairMetadadosBackup import eh_arquivo_texto, contar_linhas
from .gmet_21_GetFormataTamanho import formata_tamanho

def get_dimensoes_arquivo(self, item, loc):
    caminho = item.get("dir_atual") or item.get("dir_anterior")
    if not caminho or not os.path.exists(caminho):
        if "dimensoes" in item and item["dimensoes"]:
            return loc.traduzir_metadados(item["dimensoes"], "dimensoes")

        return ""

    with self.lock_cache:
        if caminho in self.cache_metadados:
            dados = self.cache_metadados[caminho]
            if 'dimensoes_tipo' in dados and 'dimensoes_valor' in dados:
                tipo = dados['dimensoes_tipo']
                valor = dados['dimensoes_valor']
                return f"{loc.get_text(tipo)}: {valor}"

            elif 'dimensoes' in dados:
                return loc.traduzir_metadados(dados['dimensoes'], 'dimensoes')

    ext = os.path.splitext(caminho)[1].lower()
    nome_arquivo = os.path.basename(caminho).lower()

    try:
        if ext == '.bak' in nome_arquivo or 'backup' in nome_arquivo or 'bkp' in nome_arquivo:
            if eh_arquivo_texto(caminho):
                num_linhas = contar_linhas(caminho)
                dimensoes = f"{num_linhas} {loc.get_text('lines')}"

            else:
                tamanho = os.path.getsize(caminho)
                dimensoes = f"{loc.get_text('binary_file')}: {formata_tamanho(tamanho)}"

            with self.lock_cache:
                if caminho not in self.cache_metadados:
                    self.cache_metadados[caminho] = {}

                self.cache_metadados[caminho]["dimensoes"] = dimensoes

            return loc.traduzir_metadados(dimensoes, "dimensoes")

        elif ext == '.log' or 'log' in nome_arquivo.lower():
            from .gmet_14_ExtrairMetadadosLog import extrair_metadados_log
            metadados_log = extrair_metadados_log(caminho, loc)
            
            if 'dimensoes' in metadados_log:
                with self.lock_cache:
                    if caminho not in self.cache_metadados:
                        self.cache_metadados[caminho] = {}
                    
                    self.cache_metadados[caminho]["dimensoes"] = metadados_log["dimensoes"]
                
                return metadados_log["dimensoes"]

        elif ext == '.dat':
            from .gmet_17_ExtrairMetadadosDadosEstruturados import extrair_metadados_dados_estruturados
            metadados_dat = extrair_metadados_dados_estruturados(caminho, loc)

            if 'dimensoes' in metadados_dat:
                with self.lock_cache:
                    if caminho not in self.cache_metadados:
                        self.cache_metadados[caminho] = {}

                    self.cache_metadados[caminho]["dimensoes"] = metadados_dat["dimensoes"]

                return metadados_dat["dimensoes"]

        elif ext == '.doc':
            import olefile
            if olefile.isOleFile(caminho):
                tamanho = os.path.getsize(caminho)
                paginas_estimadas = max(1, tamanho // 20000)
                dimensoes = f"{paginas_estimadas} {loc.get_text('pages_estimated')}"

                with self.lock_cache:
                    if caminho not in self.cache_metadados:
                        self.cache_metadados[caminho] = {}

                    self.cache_metadados[caminho]["dimensoes"] = dimensoes

                return dimensoes

        elif ext == '.ppt':
            import olefile
            if olefile.isOleFile(caminho):
                tamanho = os.path.getsize(caminho)
                slides_estimados = max(1, tamanho // 100000)
                dimensoes = f"{slides_estimados} {loc.get_text('slides_estimated')}"

                with self.lock_cache:
                    if caminho not in self.cache_metadados:
                        self.cache_metadados[caminho] = {}

                    self.cache_metadados[caminho]["dimensoes"] = dimensoes

                return dimensoes

        elif ext in ['.xlsx', '.xlsm']:
            from openpyxl import load_workbook
            wb = load_workbook(caminho, read_only=True, data_only=True)

            planilhas = len(wb.sheetnames)

            linhas_total = 0
            colunas_total = 0
            for sheet_name in wb.sheetnames[:3]:
                sheet = wb[sheet_name]
                if hasattr(sheet, 'max_row') and hasattr(sheet, 'max_column'):
                    linhas_total += sheet.max_row
                    if sheet.max_column > colunas_total:
                        colunas_total = sheet.max_column

            dimensoes = f"{planilhas} {loc.get_text('spreadsheets')}, ~{linhas_total} {loc.get_text('lines')}, {colunas_total} {loc.get_text('columns')}"
            wb.close()

            with self.lock_cache:
                if caminho not in self.cache_metadados:
                    self.cache_metadados[caminho] = {}

                self.cache_metadados[caminho]["dimensoes"] = dimensoes

            return dimensoes

    except Exception as e:
        print(f"Erro ao extrair dimensões diretamente: {e}")

    metadados = get_metadados(item)
    if "dimensoes" in metadados:
        return loc.traduzir_metadados(metadados.get("dimensoes", ""), "dimensoes")

    return ""
