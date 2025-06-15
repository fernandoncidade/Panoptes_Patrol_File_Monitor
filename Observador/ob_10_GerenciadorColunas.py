try:
    import os
    import sys
    import json
    import queue
    import time
    import threading
    from PySide6.QtGui import QColor
    from PySide6.QtCore import QMetaObject, Qt
    from PySide6.QtWidgets import QTableWidgetItem
    from datetime import datetime
    from concurrent.futures import ThreadPoolExecutor
    from .ob_11_GerenciadorTabela import GerenciadorTabela
    from Observador.GerenciamentoMetadados import (
        extrair_metadados_codigo_fonte,
        extrair_metadados_imagem,
        extrair_metadados_audio,
        extrair_metadados_video,
        extrair_metadados_documento,
        extrair_metadados_planilha,
        extrair_metadados_apresentacao,
        extrair_metadados_banco_dados,
        extrair_metadados_executavel,
        extrair_metadados_temporario,
        extrair_metadados_arquivo,
        extrair_metadados_backup,
        extrair_metadados_log,
        extrair_metadados_config,
        extrair_metadados_olefile,
        identificar_tipo_arquivo,
        get_tamanho_diretorio_arquivo,
        get_atributos_arquivo,
        get_autor_arquivo,
        get_dimensoes_arquivo,
        get_duracao_arquivo,
        get_taxa_bits_arquivo,
        get_protecao_arquivo
    )
except ImportError:
    pass

def obter_caminho_persistente():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)

    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_dir = os.path.join(base_path, "config")

    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)

        except Exception as e:
            print(f"Erro ao criar diretório de configuração: {e}")

    return config_dir


class GerenciadorColunas:
    def __init__(self, interface_monitor):
        self.interface = interface_monitor
        if hasattr(interface_monitor, 'loc'):
            self.loc = interface_monitor.loc

        else:
            self.loc = interface_monitor.observador.loc

        self.loc.idioma_alterado.connect(self.atualizar_interface)

        self.config_path = os.path.join(obter_caminho_persistente(), "colunas_config.json")
        print(f"Caminho de configuração das colunas: {self.config_path}")

        self.cache_metadados = {}
        self.fila_metadados = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.lock_cache = threading.Lock()
        self.processando_metadados = False
        self.gerenciador_tabela = GerenciadorTabela(interface_monitor)

        self.thread_metadados = threading.Thread(target=self.processar_fila_metadados, daemon=True)
        self.thread_metadados.start()

        self.COLUNAS_DISPONIVEIS = {
            "tipo_operacao": {
                "translation_key": "operation_type",
                "nome": self.loc.get_text("operation_type"),
                "visivel": True,
                "ordem": 0,
                "getter": lambda item: item.get("tipo_operacao", "")
            },
            "nome": {
                "translation_key": "name",
                "nome": self.loc.get_text("name"),
                "visivel": True,
                "ordem": 1,
                "getter": lambda item: item.get("nome", "")
            },
            "dir_anterior": {
                "translation_key": "prev_dir",
                "nome": self.loc.get_text("prev_dir"),
                "visivel": True,
                "ordem": 2,
                "getter": lambda item: item.get("dir_anterior", "")
            },
            "dir_atual": {
                "translation_key": "curr_dir",
                "nome": self.loc.get_text("curr_dir"),
                "visivel": True,
                "ordem": 3,
                "getter": lambda item: item.get("dir_atual", "")
            },
            "data_criacao": {
                "translation_key": "creation_date",
                "nome": self.loc.get_text("creation_date"),
                "visivel": False,
                "ordem": 4,
                "getter": lambda item: item.get("data_criacao", "")
            },
            "data_modificacao": {
                "translation_key": "modification_date",
                "nome": self.loc.get_text("modification_date"),
                "visivel": True,
                "ordem": 6,
                "getter": lambda item: item.get("data_modificacao", "")
            },
            "data_acesso": {
                "translation_key": "access_date",
                "nome": self.loc.get_text("access_date"),
                "visivel": False,
                "ordem": 7,
                "getter": lambda item: item.get("data_acesso", "")
            },
            "tipo": {
                "translation_key": "type",
                "nome": self.loc.get_text("type"),
                "visivel": True,
                "ordem": 8,
                "getter": lambda item: item.get("tipo", "")
            },
            "tamanho": {
                "translation_key": "size",
                "nome": self.loc.get_text("size"),
                "visivel": False,
                "ordem": 9,
                "getter": lambda item: get_tamanho_diretorio_arquivo(self, item, self.loc)
            },
            "atributos": {
                "translation_key": "attributes",
                "nome": self.loc.get_text("attributes"),
                "visivel": False,
                "ordem": 10,
                "getter": lambda item: get_atributos_arquivo(item, self.loc)
            },
            "autor": {
                "translation_key": "author",
                "nome": self.loc.get_text("author"),
                "visivel": False,
                "ordem": 11,
                "getter": lambda item: get_autor_arquivo(item, self.loc)
            },
            "dimensoes": {
                "translation_key": "dimensions",
                "nome": self.loc.get_text("dimensions"),
                "visivel": False,
                "ordem": 12,
                "getter": lambda item: get_dimensoes_arquivo(self, item, self.loc)
            },
            "duracao": {
                "translation_key": "duration",
                "nome": self.loc.get_text("duration"),
                "visivel": False,
                "ordem": 13,
                "getter": lambda item: get_duracao_arquivo(self, item)
            },
            "taxa_bits": {
                "translation_key": "bit_rate",
                "nome": self.loc.get_text("bit_rate"),
                "visivel": False,
                "ordem": 14,
                "getter": lambda item: get_taxa_bits_arquivo(self, item)
            },
            "protegido": {
                "translation_key": "protected",
                "nome": self.loc.get_text("protected"),
                "visivel": False,
                "ordem": 15,
                "getter": lambda item: get_protecao_arquivo(self, item, self.loc)
            },
            "paginas": {
                "translation_key": "pages",
                "nome": self.loc.get_text("pages"),
                "visivel": False,
                "ordem": 16,
                "getter": lambda item: item.get("paginas", "")
            },
            "linhas": {
                "translation_key": "lines",
                "nome": self.loc.get_text("lines"),
                "visivel": False,
                "ordem": 17,
                "getter": lambda item: item.get("linhas", "")
            },
            "palavras": {
                "translation_key": "words",
                "nome": self.loc.get_text("words"),
                "visivel": False,
                "ordem": 18,
                "getter": lambda item: item.get("palavras", "")
            },
            "paginas_estimadas": {
                "translation_key": "pages_estimated",
                "nome": self.loc.get_text("pages_estimated"),
                "visivel": False,
                "ordem": 19,
                "getter": lambda item: item.get("paginas_estimadas", "")
            },
            "linhas_codigo": {
                "translation_key": "lines_code",
                "nome": self.loc.get_text("lines_code"),
                "visivel": False,
                "ordem": 20,
                "getter": lambda item: item.get("linhas_codigo", "")
            },
            "total_linhas": {
                "translation_key": "total_lines",
                "nome": self.loc.get_text("total_lines"),
                "visivel": False,
                "ordem": 21,
                "getter": lambda item: item.get("total_linhas", "")
            },
            "slides_estimados": {
                "translation_key": "slides_estimated",
                "nome": self.loc.get_text("slides_estimated"),
                "visivel": False,
                "ordem": 22,
                "getter": lambda item: item.get("slides_estimados", "")
            },
            "arquivos": {
                "translation_key": "files",
                "nome": self.loc.get_text("files"),
                "visivel": False,
                "ordem": 23,
                "getter": lambda item: item.get("arquivos", "")
            },
            "descompactados": {
                "translation_key": "unzipped",
                "nome": self.loc.get_text("unzipped"),
                "visivel": False,
                "ordem": 24,
                "getter": lambda item: item.get("descompactados", "")
            },
            "slides": {
                "translation_key": "slides",
                "nome": self.loc.get_text("slides"),
                "visivel": False,
                "ordem": 25,
                "getter": lambda item: item.get("slides", "")
            },
            "binario": {
                "translation_key": "binary_file",
                "nome": self.loc.get_text("binary_file"),
                "visivel": False,
                "ordem": 26,
                "getter": lambda item: item.get("binario", "")
            },
            "planilhas": {
                "translation_key": "spreadsheets",
                "nome": self.loc.get_text("spreadsheets"),
                "visivel": False,
                "ordem": 27,
                "getter": lambda item: item.get("planilhas", "")
            },
            "colunas": {
                "translation_key": "columns",
                "nome": self.loc.get_text("columns"),
                "visivel": False,
                "ordem": 28,
                "getter": lambda item: item.get("colunas", "")
            },
            "registros": {
                "translation_key": "records",
                "nome": self.loc.get_text("records"),
                "visivel": False,
                "ordem": 29,
                "getter": lambda item: item.get("registros", "")
            },
            "tabelas": {
                "translation_key": "tables",
                "nome": self.loc.get_text("tables"),
                "visivel": False,
                "ordem": 30,
                "getter": lambda item: item.get("tabelas", "")
            }
        }

        self.carregar_configuracoes()

    def atualizar_interface(self, idioma: str):
        for key, coluna in self.COLUNAS_DISPONIVEIS.items():
            tk = coluna.get("translation_key", key)
            self.COLUNAS_DISPONIVEIS[key]["nome"] = self.loc.get_text(tk)

        with self.lock_cache:
            self.cache_metadados.clear()

        if hasattr(self.interface, 'gerenciador_tabela'):
            self.interface.gerenciador_tabela.atualizar_dados_tabela(self.interface.tabela_dados)

        else:
            self.gerenciador_tabela.configurar_tabela(self.interface.tabela_dados)

    def salvar_estado_tabela(self, tabela):
        eventos = []
        for row in range(tabela.rowCount()):
            evento = {}
            for col in range(tabela.columnCount()):
                header = tabela.horizontalHeaderItem(col).text()
                item = tabela.item(row, col)
                if item:
                    evento[header] = item.text()

            eventos.append(evento)

        return eventos

    def restaurar_estado_tabela(self, tabela, eventos):
        tabela.clearContents()
        tabela.setRowCount(len(eventos))

        colunas_visiveis = [(key, col) for key, col in sorted(self.COLUNAS_DISPONIVEIS.items(), key=lambda x: x[1]["ordem"]) if col["visivel"]]

        for row, evento in enumerate(eventos):
            for col, (key, coluna) in enumerate(colunas_visiveis):
                valor = evento.get(coluna["nome"], "")
                item = QTableWidgetItem(str(valor))

                if key == "tipo_operacao":
                    cores = {
                        self.loc.get_text("op_renamed"): QColor(0, 255, 0),
                        self.loc.get_text("op_added"): QColor(0, 0, 255), 
                        self.loc.get_text("op_deleted"): QColor(255, 0, 0),
                        self.loc.get_text("op_modified"): QColor(255, 98, 0),
                        self.loc.get_text("op_moved"): QColor(255, 0, 255),
                        self.loc.get_text("op_scanned"): QColor(128, 128, 128)
                    }

                    item.setBackground(cores.get(valor, QColor(255, 255, 255)))

                tabela.setItem(row, col, item)

    def carregar_configuracoes(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config = json.load(f)

                for k, v in config.items():
                    if k in self.COLUNAS_DISPONIVEIS:
                        self.COLUNAS_DISPONIVEIS[k]["visivel"] = v["visivel"]
                        self.COLUNAS_DISPONIVEIS[k]["ordem"] = v["ordem"]

        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")

    def salvar_configuracoes(self):
        config = {k: {"visivel": v["visivel"], "ordem": v["ordem"]} for k, v in self.COLUNAS_DISPONIVEIS.items()}

        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)

        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")

    def processar_fila_metadados(self):
        while True:
            try:
                item = self.fila_metadados.get(timeout=1)
                caminho = item.get("dir_atual") or item.get("dir_anterior")

                if not caminho or not os.path.exists(caminho):
                    continue

                time.sleep(0.1)

                if os.path.exists(caminho):
                    metadados = self.get_metadados(item)

                    if metadados:
                        with self.lock_cache:
                            self.cache_metadados[caminho] = metadados

                        QMetaObject.invokeMethod(self.interface, "atualizar_colunas_tabela", Qt.QueuedConnection)

            except queue.Empty:
                continue

            except Exception as e:
                print(f"Erro no processamento de metadados: {e}")

    def callback_metadados(self, futuro):
        try:
            caminho, metadados = futuro.result()
            with self.lock_cache:
                self.cache_metadados[caminho] = metadados

            self.interface.atualizar_status()

        except Exception as e:
            print(f"Erro no callback: {e}")

    def configurar_tabela(self, tabela):
        self.gerenciador_tabela.configurar_tabela(tabela)

    def mostrar_dialogo_configuracao(self, pos=None):
        self.gerenciador_tabela.mostrar_dialogo_configuracao(pos)

    def get_metadados(self, item):
        try:
            from Observador.GerenciamentoMetadados.gmet_21_GetFormataTamanho import get_formata_tamanho

            caminho = item.get("dir_atual") or item.get("dir_anterior")
            if not caminho or not os.path.exists(caminho):
                return {}

            with self.lock_cache:
                if caminho in self.cache_metadados:
                    for campo in [
                        "paginas", "linhas", "palavras", "paginas_estimadas",
                        "linhas_codigo", "total_linhas", "slides_estimados",
                        "arquivos", "descompactados", "slides", "binario",
                        "planilhas", "colunas", "registros", "tabelas"
                    ]:
                        if campo in self.cache_metadados[caminho]:
                            item[campo] = self.cache_metadados[caminho][campo]

                    return self.cache_metadados[caminho]

            if os.path.exists(caminho):
                stats = os.stat(caminho)

                metadados = {
                    "tamanho": get_formata_tamanho(stats.st_size),
                    "data_acesso": datetime.fromtimestamp(stats.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
                    "data_modificacao": datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "data_criacao": datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                }

                try:
                    tipo = identificar_tipo_arquivo(caminho, self.loc)
                    metadados["tipo"] = tipo

                    ext = os.path.splitext(caminho)[1].lower()
                    if ext == '.dat':
                        from Observador.GerenciamentoMetadados.gmet_17_ExtrairMetadadosDadosEstruturados import extrair_metadados_dados_estruturados
                        metadados_dat = extrair_metadados_dados_estruturados(caminho, self.loc)
                        metadados.update(metadados_dat)

                    elif os.path.isfile(caminho):
                        if tipo == self.loc.get_text("file_image"):
                            metadados.update(extrair_metadados_imagem(self, caminho))

                        elif tipo == self.loc.get_text("file_audio"):
                            metadados.update(extrair_metadados_audio(self, caminho))

                        elif tipo == self.loc.get_text("file_video"):
                            metadados.update(extrair_metadados_video(self, caminho))

                        elif tipo == self.loc.get_text("file_document"):
                            metadados.update(extrair_metadados_documento(caminho, self.loc))

                        elif tipo == self.loc.get_text("file_spreadsheet"):
                            metadados.update(extrair_metadados_planilha(caminho, self.loc))

                        elif tipo == self.loc.get_text("file_presentation"):
                            metadados.update(extrair_metadados_apresentacao(caminho, self.loc))

                        elif tipo == self.loc.get_text("file_database"):
                            metadados.update(extrair_metadados_banco_dados(caminho, self.loc))

                        elif tipo == self.loc.get_text("file_executable"):
                            metadados.update(extrair_metadados_executavel(self, caminho))

                        elif tipo == self.loc.get_text("file_source_code"):
                            metadados.update(extrair_metadados_codigo_fonte(caminho, self.loc))

                        elif tipo == self.loc.get_text("file_temp"):
                            metadados.update(extrair_metadados_temporario(caminho, self.loc))

                        elif tipo == self.loc.get_text("file_archive"):
                            metadados.update(extrair_metadados_arquivo(caminho, self.loc))

                        elif tipo == self.loc.get_text("file_backup"):
                            metadados.update(extrair_metadados_backup(caminho, self.loc))

                        elif tipo == self.loc.get_text("file_log"):
                            metadados.update(extrair_metadados_log(caminho, self.loc))

                        elif tipo == self.loc.get_text("file_config"):
                            metadados.update(extrair_metadados_config(caminho, self.loc))

                        ext = os.path.splitext(caminho)[1].lower()
                        if ext in ['.doc', '.xls', '.ppt', '.msg']:
                            metadados.update(extrair_metadados_olefile(caminho, self.loc))

                    metadados["atributos"] = get_atributos_arquivo(item, self.loc)
                    metadados["autor"] = get_autor_arquivo(item, self.loc)
                    metadados["protegido"] = get_protecao_arquivo(self, item, self.loc)

                    get_dimensoes_arquivo(self, item, self.loc)

                    with self.lock_cache:
                        if caminho in self.cache_metadados:
                            for campo in [
                                "paginas", "linhas", "palavras", "paginas_estimadas",
                                "linhas_codigo", "total_linhas", "slides_estimados",
                                "arquivos", "descompactados", "slides", "binario",
                                "planilhas", "colunas", "registros", "tabelas"
                            ]:
                                if campo in self.cache_metadados[caminho]:
                                    metadados[campo] = self.cache_metadados[caminho][campo]
                                    item[campo] = self.cache_metadados[caminho][campo]

                except Exception as e:
                    print(f"Erro ao extrair metadados específicos: {e}")

                with self.lock_cache:
                    self.cache_metadados[caminho] = metadados

                for campo, valor in metadados.items():
                    item[campo] = valor

                return metadados

            return {}

        except Exception as e:
            print(f"Erro ao obter metadados: {e}")
            return {}
