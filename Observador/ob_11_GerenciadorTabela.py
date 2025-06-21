import os
import sqlite3
import threading
import textwrap
from PySide6.QtWidgets import QHeaderView, QTableWidgetItem, QApplication, QMenu
from PySide6.QtGui import QFontMetrics, QColor, QAction, QCursor
from PySide6.QtCore import QTimer, Qt
from utils.LogManager import LogManager

logger = LogManager.get_logger()


class GerenciadorTabela:
    def __init__(self, interface_monitor):
        self.interface = interface_monitor
        self.lock_db = threading.Lock()
        self.loc = interface_monitor.loc
        self.loc.idioma_alterado.connect(self.atualizar_cabecalhos)
        self.timer_atualizacao = QTimer()
        self.timer_atualizacao.timeout.connect(self.atualizar_visualizacao_tabela)
        self.timer_atualizacao.start(500)
        self.atualizacao_pendente = False
        self.texto_original_cabecalhos = {}

    def calcular_cor_texto_ideal(self, cor_fundo):
        r, g, b = cor_fundo.red(), cor_fundo.green(), cor_fundo.blue()
        luminosidade = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return QColor(255, 255, 255) if luminosidade < 0.5 else QColor(0, 0, 0)

    def atualizar_visualizacao_tabela(self):
        if hasattr(self.interface, 'tabela_dados') and self.atualizacao_pendente:
            self.interface.tabela_dados.viewport().update()
            QApplication.processEvents()
            self.atualizacao_pendente = False

    def atualizar_cabecalhos(self, idioma: str):
        if hasattr(self.interface, 'tabela_dados'):
            tabela = self.interface.tabela_dados

            self.configurar_tabela(tabela)
            self.aplicar_quebra_linha_todos_cabecalhos(tabela)
            self.ajustar_altura_cabecalho(tabela)

            logger.info(f"Cabeçalhos atualizados para o idioma: {idioma}")

            tabela.viewport().update()
            QApplication.processEvents()

    def configurar_tabela(self, tabela_dados):
        colunas_visiveis = [(key, col) for key, col in sorted(self.interface.gerenciador_colunas.COLUNAS_DISPONIVEIS.items(), key=lambda x: x[1]["ordem"]) if col["visivel"]]

        tabela_dados.setColumnCount(len(colunas_visiveis))

        self.texto_original_cabecalhos = {}
        headers = []
        for i, (key, coluna) in enumerate(colunas_visiveis):
            texto = coluna["nome"]
            self.texto_original_cabecalhos[i] = texto
            headers.append(texto)

        tabela_dados.setHorizontalHeaderLabels(headers)

        header = tabela_dados.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionsMovable(True)
        header.setHighlightSections(True)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setTextElideMode(Qt.ElideNone)

        font = header.font()
        font.setBold(True)
        header.setFont(font)

        self.ajustar_larguras_colunas(tabela_dados, colunas_visiveis)
        header.sectionResized.connect(self.redimensionar_cabecalho)
        self.aplicar_quebra_linha_todos_cabecalhos(tabela_dados)
        self.atualizar_dados_tabela(tabela_dados)
        tabela_dados.viewport().update()
        QApplication.processEvents()

    def ajustar_larguras_colunas(self, tabela_dados, colunas_visiveis):
        header = tabela_dados.horizontalHeader()
        font = header.font()
        font_metrics = QFontMetrics(font)

        PADDING = 40
        MIN_WIDTH = 10
        MAX_WIDTH = 350

        self.larguras_calculadas = {}

        for i, (key, coluna) in enumerate(colunas_visiveis):
            texto_cabecalho = coluna["nome"]

            texto_largura = font_metrics.horizontalAdvance(texto_cabecalho)

            max_content_width = 0
            for row in range(min(10, tabela_dados.rowCount())):
                item = tabela_dados.item(row, i)
                if item and item.text():
                    content_width = font_metrics.horizontalAdvance(item.text())
                    max_content_width = max(max_content_width, content_width)

            largura_total = max(texto_largura, max_content_width) + PADDING
            largura_ideal = min(max(largura_total, MIN_WIDTH), MAX_WIDTH)
            self.larguras_calculadas[i] = largura_ideal

            tabela_dados.setColumnWidth(i, largura_ideal)
            header.setSectionResizeMode(i, QHeaderView.Interactive)

            item = tabela_dados.horizontalHeaderItem(i)
            if item:
                item.setTextAlignment(Qt.AlignCenter)

    def redimensionar_cabecalho(self, logicalIndex, oldSize, newSize):
        if hasattr(self.interface, 'tabela_dados'):
            self.aplicar_quebra_linha_cabecalho(self.interface.tabela_dados, logicalIndex)
            self.ajustar_altura_cabecalho(self.interface.tabela_dados)

    def aplicar_quebra_linha_cabecalho(self, tabela, coluna_index):
        if coluna_index not in self.texto_original_cabecalhos:
            return

        texto_original = self.texto_original_cabecalhos[coluna_index]
        largura_coluna = tabela.columnWidth(coluna_index)

        font_metrics = QFontMetrics(tabela.horizontalHeader().font())

        padding = 10
        espaco_disponivel = largura_coluna - padding

        char_width = font_metrics.averageCharWidth()
        max_chars = max(1, int(espaco_disponivel / char_width))

        texto_quebrado = textwrap.fill(texto_original, width=max_chars, break_long_words=False, break_on_hyphens=True)

        item = tabela.horizontalHeaderItem(coluna_index)
        if item:
            item.setText(texto_quebrado)
            item.setTextAlignment(Qt.AlignCenter)

    def aplicar_quebra_linha_todos_cabecalhos(self, tabela):
        for i in range(tabela.columnCount()):
            self.aplicar_quebra_linha_cabecalho(tabela, i)

        self.ajustar_altura_cabecalho(tabela)

    def ajustar_altura_cabecalho(self, tabela):
        header = tabela.horizontalHeader()
        font_metrics = QFontMetrics(header.font())

        max_linhas = 1
        for i in range(tabela.columnCount()):
            item = tabela.horizontalHeaderItem(i)
            if item:
                texto = item.text()
                linhas = texto.count('\n') + 1
                max_linhas = max(max_linhas, linhas)

        altura_linha = font_metrics.height()
        altura_necessaria = max_linhas * altura_linha + 10

        header.setMinimumHeight(altura_necessaria)
        header.setMaximumHeight(altura_necessaria)

    def atualizar_dados_tabela(self, tabela_dados, row_especifico=None):
        try:
            db_path = self.interface.evento_base.db_path
            with self.lock_db:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    conn.execute('PRAGMA journal_mode = WAL')
                    conn.execute('PRAGMA synchronous = NORMAL')
                    conn.execute('PRAGMA cache_size = 100000')
                    conn.execute('PRAGMA temp_store = MEMORY')
                    conn.execute('PRAGMA page_size = 16384')
                    conn.execute('PRAGMA mmap_size = 4294967296')

                    colunas_visiveis = [(key, col) for key, col in sorted(self.interface.gerenciador_colunas.COLUNAS_DISPONIVEIS.items(), key=lambda x: x[1]["ordem"]) if col["visivel"]]

                    cores = {}
                    if hasattr(self.interface, 'gerenciador_menus_ui') and hasattr(self.interface.gerenciador_menus_ui, 'gerenciador_cores'):
                        gerenciador_cores = self.interface.gerenciador_menus_ui.gerenciador_cores
                        cores = {
                            self.interface.loc.get_text("op_renamed"): gerenciador_cores.obter_cor_qcolor("op_renamed"),
                            self.interface.loc.get_text("op_added"): gerenciador_cores.obter_cor_qcolor("op_added"), 
                            self.interface.loc.get_text("op_deleted"): gerenciador_cores.obter_cor_qcolor("op_deleted"),
                            self.interface.loc.get_text("op_modified"): gerenciador_cores.obter_cor_qcolor("op_modified"),
                            self.interface.loc.get_text("op_moved"): gerenciador_cores.obter_cor_qcolor("op_moved"),
                            self.interface.loc.get_text("op_scanned"): gerenciador_cores.obter_cor_qcolor("op_scanned")
                        }

                    else:
                        cores = {
                            self.interface.loc.get_text("op_renamed"): QColor(0, 255, 0),
                            self.interface.loc.get_text("op_added"): QColor(0, 0, 255),
                            self.interface.loc.get_text("op_deleted"): QColor(255, 0, 0),
                            self.interface.loc.get_text("op_modified"): QColor(255, 98, 0),
                            self.interface.loc.get_text("op_moved"): QColor(255, 0, 255),
                            self.interface.loc.get_text("op_scanned"): QColor(128, 128, 128)
                        }

                    cor_padrao = QColor(255, 255, 255)

                    try:
                        if row_especifico is not None:
                            cursor.execute("""
                                SELECT * FROM monitoramento 
                                WHERE id = (SELECT id FROM monitoramento ORDER BY id DESC LIMIT 1 OFFSET ?)
                            """, (row_especifico,))

                        else:
                            cursor.execute("CREATE INDEX IF NOT EXISTS idx_monitoramento_id ON monitoramento(id)")
                            cursor.execute("SELECT * FROM monitoramento ORDER BY id DESC")

                        registros = cursor.fetchall()
                        colunas_db = [desc[0] for desc in cursor.description]

                        total_registros = len(registros)

                        if hasattr(self.interface, 'atualizar_contador_eventos'):
                            self.interface.atualizar_contador_eventos(total_registros)

                        if not row_especifico:
                            tabela_dados.setRowCount(total_registros)

                        getters = {key: getattr(self.interface.gerenciador_colunas, f"get_{key}", None)
                                   for key, _ in colunas_visiveis}

                        for idx, registro in enumerate(registros):
                            row = idx if row_especifico is None else row_especifico
                            evento = dict(zip(colunas_db, registro))

                            for col, (key, _) in enumerate(colunas_visiveis):
                                try:
                                    getter = getters[key]
                                    valor = getter(evento) if getter else evento.get(key, "")

                                    if key == "tipo_operacao" and valor:
                                        valor = self.loc.traduzir_tipo_operacao(valor)

                                    elif key in ["tipo", "atributos", "autor", "dimensoes", "duracao", "taxa_bits", "protegido", "paginas", "linhas", "palavras", "palavras_estimadas", 
                                                 "linhas_codigo", "total_linhas", "slides_estimados", "arquivos", "descompactados", "slides", "binario", "planilhas", "colunas", "registros", "tabelas"]:
                                        valor = self.loc.traduzir_metadados(valor, key)

                                    if key in ["dir_anterior", "dir_atual"] and valor:
                                        valor = os.path.normpath(str(valor)).replace('/', '\\')
                                        if valor == ".":
                                            valor = ""

                                    novo_texto = str(valor)
                                    item = tabela_dados.item(row, col)

                                    if item is None:
                                        item = QTableWidgetItem(novo_texto)
                                        if key == "tipo_operacao":
                                            cor = cores.get(valor, cor_padrao)
                                            item.setBackground(cor)
                                            cor_texto = self.calcular_cor_texto_ideal(cor)
                                            item.setForeground(cor_texto)

                                        tabela_dados.setItem(row, col, item)

                                    else:
                                        if item.text() != novo_texto:
                                            item.setText(novo_texto)

                                        if key == "tipo_operacao":
                                            nova_cor = cores.get(valor, cor_padrao)
                                            if item.background().color() != nova_cor:
                                                item.setBackground(nova_cor)
                                                cor_texto = self.calcular_cor_texto_ideal(nova_cor)
                                                item.setForeground(cor_texto)

                                except Exception as e:
                                    print(f"Erro ao processar coluna {key}: {e}")
                                    if not tabela_dados.item(row, col):
                                        tabela_dados.setItem(row, col, QTableWidgetItem(""))

                    except Exception as e:
                        print(f"Erro durante processamento: {e}")
                        raise

        except Exception as e:
            print(f"Erro crítico ao atualizar dados da tabela: {e}")

        finally:
            tabela_dados.viewport().update()
            QApplication.processEvents()
            self.atualizacao_pendente = True

    def atualizar_linha_mais_recente(self, tabela_dados):
        try:
            db_path = self.interface.evento_base.db_path
            with self.lock_db:
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    conn.execute('PRAGMA journal_mode = WAL')
                    conn.execute('PRAGMA synchronous = NORMAL')

                    cursor.execute("SELECT * FROM monitoramento ORDER BY id DESC LIMIT 1")
                    registro = cursor.fetchone()

                    if not registro:
                        return

                    colunas_db = [desc[0] for desc in cursor.description]
                    evento = dict(zip(colunas_db, registro))

                    tabela_dados.insertRow(0)

                    colunas_visiveis = [(key, col) for key, col in sorted(self.interface.gerenciador_colunas.COLUNAS_DISPONIVEIS.items(), key=lambda x: x[1]["ordem"]) if col["visivel"]]

                    cores = {}
                    if hasattr(self.interface, 'gerenciador_menus_ui') and hasattr(self.interface.gerenciador_menus_ui, 'gerenciador_cores'):
                        gerenciador_cores = self.interface.gerenciador_menus_ui.gerenciador_cores
                        cores = {
                            self.interface.loc.get_text("op_renamed"): gerenciador_cores.obter_cor_qcolor("op_renamed"),
                            self.interface.loc.get_text("op_added"): gerenciador_cores.obter_cor_qcolor("op_added"), 
                            self.interface.loc.get_text("op_deleted"): gerenciador_cores.obter_cor_qcolor("op_deleted"),
                            self.interface.loc.get_text("op_modified"): gerenciador_cores.obter_cor_qcolor("op_modified"),
                            self.interface.loc.get_text("op_moved"): gerenciador_cores.obter_cor_qcolor("op_moved"),
                            self.interface.loc.get_text("op_scanned"): gerenciador_cores.obter_cor_qcolor("op_scanned")
                        }

                    else:
                        cores = {
                            self.interface.loc.get_text("op_renamed"): QColor(0, 255, 0),
                            self.interface.loc.get_text("op_added"): QColor(0, 0, 255),
                            self.interface.loc.get_text("op_deleted"): QColor(255, 0, 0),
                            self.interface.loc.get_text("op_modified"): QColor(255, 98, 0),
                            self.interface.loc.get_text("op_moved"): QColor(255, 0, 255),
                            self.interface.loc.get_text("op_scanned"): QColor(128, 128, 128)
                        }

                    cor_padrao = QColor(255, 255, 255)

                    getters = {key: getattr(self.interface.gerenciador_colunas, f"get_{key}", None)
                               for key, _ in colunas_visiveis}

                    for col, (key, _) in enumerate(colunas_visiveis):
                        try:
                            getter = getters[key]
                            valor = getter(evento) if getter else evento.get(key, "")

                            if key == "tipo_operacao" and valor:
                                valor = self.loc.traduzir_tipo_operacao(valor)

                            elif key in ["tipo", "atributos", "autor", "dimensoes", "duracao", "taxa_bits", "protegido", "paginas", "linhas", "palavras", "palavras_estimadas", 
                                         "linhas_codigo", "total_linhas", "slides_estimados", "arquivos", "descompactados", "slides", "binario", "planilhas", "colunas", "registros", "tabelas"]:
                                valor = self.loc.traduzir_metadados(valor, key)

                            if key in ["dir_anterior", "dir_atual"] and valor:
                                valor = os.path.normpath(str(valor)).replace('/', '\\')
                                if valor == ".":
                                    valor = ""

                            novo_texto = str(valor)

                            item = QTableWidgetItem(novo_texto)
                            if key == "tipo_operacao":
                                cor = cores.get(valor, cor_padrao)
                                item.setBackground(cor)
                                cor_texto = self.calcular_cor_texto_ideal(cor)
                                item.setForeground(cor_texto)

                            tabela_dados.setItem(0, col, item)

                        except Exception as e:
                            print(f"Erro ao processar coluna {key}: {e}")
                            if not tabela_dados.item(0, col):
                                tabela_dados.setItem(0, col, QTableWidgetItem(""))

                    if hasattr(self.interface, 'atualizar_contador_eventos'):
                        cursor.execute("SELECT COUNT(*) FROM monitoramento")
                        total = cursor.fetchone()[0]
                        self.interface.atualizar_contador_eventos(total)

        except Exception as e:
            print(f"Erro crítico ao atualizar linha mais recente: {e}")

        finally:
            tabela_dados.viewport().update()
            QApplication.processEvents()
            self.atualizacao_pendente = True

    def mostrar_dialogo_configuracao(self, pos=None):
        menu = QMenu()
        menu.setToolTipsVisible(True)

        titulo = QAction(self.loc.get_text("configure_columns"), menu)
        titulo.setEnabled(False)
        menu.addAction(titulo)
        menu.addSeparator()

        acoes = {}
        for key, coluna in sorted(self.interface.gerenciador_colunas.COLUNAS_DISPONIVEIS.items(), key=lambda x: x[1]["ordem"]):
            acao = QAction(coluna["nome"], menu)
            acao.setCheckable(True)
            acao.setChecked(coluna["visivel"])
            acao.setData(key)
            acao.setToolTip(f"Mostrar/ocultar coluna {coluna['nome']}")
            acoes[key] = acao
            menu.addAction(acao)

        menu.aboutToShow.connect(lambda: menu.move(QCursor.pos()))
        pos = pos or QCursor.pos()

        if menu.exec(pos):
            tabela = self.interface.tabela_dados
            for key, acao in acoes.items():
                self.interface.gerenciador_colunas.COLUNAS_DISPONIVEIS[key]["visivel"] = acao.isChecked()

            self.interface.gerenciador_colunas.salvar_configuracoes()
            self.configurar_tabela(tabela)

            if hasattr(self.interface, 'atualizar_status'):
                self.interface.atualizar_status()
