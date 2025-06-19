import os
import sys
from utils.LogManager import LogManager
import sqlite3
import subprocess
from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QFontMetrics, QFont
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QWidget, QPushButton,
                               QMessageBox, QFileDialog, QApplication,
                               QCheckBox, QScrollArea, QFrame,
                               QSplitter, QLabel)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

logger = LogManager.get_logger()


class GerenciadorEstatisticasUI:
    def __init__(self, interface_principal):
        self.interface = interface_principal
        self.loc = interface_principal.loc
        self.evento_base = interface_principal.evento_base
        self.dialog_estatisticas = None
        self.checkboxes_graficos = {}
        self.tab_widget = None
        self.graficos_dados = {}
        self.painel_selecao = None
        self.splitter = None

        if hasattr(self.loc, 'idioma_alterado'):
            self.loc.idioma_alterado.connect(self.atualizar_graficos_apos_mudanca_idioma)

    def mostrar_estatisticas(self):
        base_path = getattr(sys, "_MEIPASS", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        icon_path = os.path.join(base_path, "icones")
        logger.debug(f"Caminho dos ícones: {icon_path}")
        logger.debug(f"Arquivo de ícone existe? {os.path.exists(os.path.join(icon_path, 'salvar.ico'))}")

        try:
            if self.dialog_estatisticas and self.dialog_estatisticas.isVisible():
                self.dialog_estatisticas.raise_()
                self.dialog_estatisticas.activateWindow()
                return

            logger.info("Gerando estatísticas")

            try:
                with sqlite3.connect(self.evento_base.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT COUNT(*) FROM monitoramento")
                    count = cursor.fetchone()[0]

                    if count == 0:
                        logger.warning("Não há dados para gerar estatísticas")
                        QMessageBox.warning(self.interface, self.loc.get_text("warning"), self.loc.get_text("no_data_to_plot"))
                        return

            except Exception as e:
                logger.error(f"Erro ao verificar quantidade de dados: {e}", exc_info=True)
                QMessageBox.critical(self.interface, self.loc.get_text("error"), 
                                     f"{self.loc.get_text('stats_error')}: {str(e)}")
                return

            self.dialog_estatisticas = QDialog(None)  

            self.dialog_estatisticas.setWindowFlags(
                Qt.Window |                   
                Qt.WindowSystemMenuHint |     
                Qt.WindowMinMaxButtonsHint |  
                Qt.WindowCloseButtonHint      
            )

            self.dialog_estatisticas.finished.connect(self.limpar_referencia_dialog)

            estatisticas_icon = QIcon(os.path.join(icon_path, "statistics.ico"))
            self.dialog_estatisticas.setWindowIcon(estatisticas_icon)
            self.dialog_estatisticas.setWindowTitle(self.loc.get_text("statistics"))
            self.dialog_estatisticas.setMinimumSize(1000, 700)

            main_layout = QHBoxLayout()

            self.splitter = QSplitter(Qt.Horizontal)

            from Estatistica.st_01_GeradorEstatisticas import GeradorEstatisticas
            self.gerador_atual = GeradorEstatisticas(self.evento_base.db_path, self.loc, self.interface)
            gerador = self.gerador_atual

            graficos = self._criar_lista_graficos(gerador)

            self.painel_selecao = self._criar_painel_selecao(graficos)
            self.splitter.addWidget(self.painel_selecao)

            graphics_panel = self._criar_painel_graficos()
            self.splitter.addWidget(graphics_panel)

            self.splitter.setSizes([300, 700])

            main_layout.addWidget(self.splitter)
            self.dialog_estatisticas.setLayout(main_layout)

            QApplication.setOverrideCursor(Qt.WaitCursor)

            try:
                logger.debug("Obtendo dados para estatísticas")
                df = gerador._obter_dados()

                if df.empty:
                    logger.warning("DataFrame vazio, não é possível gerar gráficos")
                    QApplication.restoreOverrideCursor()
                    QMessageBox.warning(self.interface, self.loc.get_text("warning"), self.loc.get_text("no_data_to_plot"))
                    return

                self._popular_checkboxes(graficos)
                self._gerar_todos_graficos(graficos)

                if self.tab_widget.count() == 0:
                    raise Exception(self.loc.get_text("all_graphs_failed"))

                logger.info("Dialog de estatísticas criado com sucesso")

            finally:
                QApplication.restoreOverrideCursor()

            self.dialog_estatisticas.show()

        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Erro ao mostrar estatísticas: {e}", exc_info=True)
            QMessageBox.critical(self.interface, self.loc.get_text("error"), self.loc.get_text("stats_error").format(str(e)))

    def salvar_todos_graficos(self, gerador):
        try:
            gerador.atualizar_textos_traduzidos()

            logger.info("Iniciando salvamento de todos os gráficos")
            diretorio = QFileDialog.getExistingDirectory(self.interface, self.loc.get_text("select_save_dir"), "", QFileDialog.ShowDirsOnly)

            if not diretorio:
                logger.debug("Operação de salvamento cancelada pelo usuário")
                return

            QApplication.setOverrideCursor(Qt.WaitCursor)

            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                estatisticas_texto = self.loc.get_text("statistics").replace(":", "").strip()
                diretorio_graficos = os.path.join(diretorio, f"{estatisticas_texto}_{timestamp}")
                os.makedirs(diretorio_graficos, exist_ok=True)

                graficos = self._criar_lista_graficos(gerador)
                resultados = {}
                graficos_salvos = 0

                for grafico in graficos:
                    try:
                        titulo = grafico["titulo"]
                        arquivo_destino = os.path.join(diretorio_graficos, f"{titulo}.png")
                        logger.debug(f"Salvando {titulo} em {arquivo_destino}")

                        fig = grafico["func"]()
                        fig.savefig(arquivo_destino, bbox_inches='tight', dpi=600)

                        logger.info(f"Gráfico {titulo} salvo com sucesso")
                        resultados[titulo] = True
                        graficos_salvos += 1

                    except Exception as e:
                        logger.error(f"Erro ao salvar {grafico['titulo']}: {e}", exc_info=True)
                        resultados[grafico['titulo']] = False

                QApplication.restoreOverrideCursor()

                detalhes = []
                for nome, sucesso in resultados.items():
                    status = self.loc.get_text("success") if sucesso else self.loc.get_text("failure")
                    detalhes.append(f"- {nome}: {status}")

                msg = QMessageBox(self.interface)
                msg.setWindowTitle(self.loc.get_text("graphs_saved"))
                msg.setIcon(QMessageBox.Information)
                msg.setText(self.loc.get_text("graphs_saved_detail").format(graficos_salvos, len(resultados), diretorio_graficos))
                msg.setDetailedText("\n".join(detalhes))
                msg.addButton(self.loc.get_text("ok"), QMessageBox.AcceptRole)
                btn_open = msg.addButton(self.loc.get_text("open_folder"), QMessageBox.ActionRole)

                self._traduzir_botoes_detalhes(msg)

                timer = QTimer(self.interface)
                timer.timeout.connect(lambda: self._traduzir_botoes_detalhes(msg))
                timer.start(10)

                msg.finished.connect(timer.stop)
                msg.exec()

                if msg.clickedButton() == btn_open:
                    self._abrir_diretorio(diretorio_graficos)

                logger.info(f"Gráficos salvos com sucesso: {graficos_salvos}/{len(resultados)}")

            finally:
                QApplication.restoreOverrideCursor()

        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Erro ao salvar gráficos: {e}", exc_info=True)
            QMessageBox.critical(self.interface, self.loc.get_text("error"), self.loc.get_text("save_graphs_error").format(str(e)))

    def limpar_referencia_dialog(self):
        self.dialog_estatisticas = None
        self.checkboxes_graficos.clear()
        self.graficos_dados.clear()
        self.painel_selecao = None
        self.splitter = None

    def atualizar_graficos_apos_mudanca_idioma(self, novo_idioma):
        if self.dialog_estatisticas and self.dialog_estatisticas.isVisible():
            logger.debug(f"Atualizando interface para o idioma: {novo_idioma}")

            self._ajustar_largura_painel_selecao()
            self._atualizar_graficos(self.dialog_estatisticas)

    def _criar_painel_selecao(self, graficos=None):
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)

        max_width = self._calcular_largura_ideal(graficos)

        logger.debug(f"Largura calculada para o painel de seleção: {max_width}")
        panel.setMaximumWidth(max_width)

        layout = QVBoxLayout()

        titulo = QLabel(self.loc.get_text("select_graphs") if "select_graphs" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Selecionar Gráficos")
        titulo.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        layout.addWidget(titulo)

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.checkboxes_layout = QVBoxLayout()

        self.checkbox_todos = QCheckBox(self.loc.get_text("select_all") if "select_all" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Selecionar Todos")
        self.checkbox_todos.setChecked(True)
        self.checkbox_todos.setTristate(True)
        self.checkbox_todos.clicked.connect(self._alternar_todos_checkboxes)
        self.checkbox_todos.setStyleSheet("font-weight: bold; margin: 5px;")
        self.checkboxes_layout.addWidget(self.checkbox_todos)

        separador = QFrame()
        separador.setFrameStyle(QFrame.HLine)
        self.checkboxes_layout.addWidget(separador)

        scroll_widget.setLayout(self.checkboxes_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        buttons_layout = QVBoxLayout()

        base_path = getattr(sys, "_MEIPASS", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        icon_path = os.path.join(base_path, "icones")

        btn_salvar_selecionados = QPushButton(self.loc.get_text("save_selected") if "save_selected" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Salvar Selecionados")
        btn_salvar_selecionados.setIcon(QIcon(os.path.join(icon_path, "salvar.ico")))
        btn_salvar_selecionados.clicked.connect(self._salvar_graficos_selecionados)
        buttons_layout.addWidget(btn_salvar_selecionados)

        btn_salvar_todos = QPushButton(self.loc.get_text("save_all"))
        btn_salvar_todos.setIcon(QIcon(os.path.join(icon_path, "salvar.ico")))
        btn_salvar_todos.clicked.connect(lambda: self.salvar_todos_graficos(self.gerador_atual))
        buttons_layout.addWidget(btn_salvar_todos)

        btn_atualizar = QPushButton(self.loc.get_text("refresh"))
        btn_atualizar.setIcon(QIcon(os.path.join(icon_path, "atualizar.ico")))
        btn_atualizar.clicked.connect(lambda: self._atualizar_graficos(self.dialog_estatisticas))
        buttons_layout.addWidget(btn_atualizar)

        layout.addLayout(buttons_layout)
        panel.setLayout(layout)

        return panel

    def _criar_painel_graficos(self):
        self.tab_widget = QTabWidget()
        return self.tab_widget

    def _criar_lista_graficos(self, gerador):
        return [
            {"titulo": self.loc.get_text("operations_pie"), 
             "func": gerador.grafico_operacoes_pizza},

            {"titulo": self.loc.get_text("file_types"), 
             "func": gerador.grafico_tipos_arquivo_barras},

            {"titulo": self.loc.get_text("timeline"), 
             "func": gerador.grafico_timeline_operacoes},

            {"titulo": self.loc.get_text("tree_map"), 
             "func": gerador.grafico_treemap_tipos},

            {"titulo": self.loc.get_text("hour_histogram"), 
             "func": gerador.grafico_histograma_horarios},

            {"titulo": self.loc.get_text("pareto_analysis"), 
             "func": gerador.grafico_pareto_operacoes},

            {"titulo": self.loc.get_text("operations_by_day"), 
             "func": gerador.grafico_cluster_linha},

            {"titulo": self.loc.get_text("size_distribution"), 
            "func": gerador.grafico_boxplot_distribuicao},

            {"titulo": self.loc.get_text("events_monitored"), 
             "func": gerador.grafico_boxplot_eventos},

            {"titulo": self.loc.get_text("temporal_distribution"), 
             "func": gerador.grafico_heatmap},

            {"titulo": self.loc.get_text("file_size_analysis"), 
             "func": gerador.grafico_scatter},

            {"titulo": self.loc.get_text("file_operations_flow"), 
             "func": gerador.grafico_sankey},

            {"titulo": self.loc.get_text("operations_by_file_type"), 
             "func": gerador.grafico_radar},

            {"titulo": self.loc.get_text("file_size_distribution"), 
             "func": gerador.grafico_dotplot}
        ]

    def _popular_checkboxes(self, graficos):
        logger.debug(f"Populando {len(graficos)} checkboxes")

        self.checkboxes_graficos.clear()

        while self.checkboxes_layout.count() > 2:
            child = self.checkboxes_layout.takeAt(2)
            if child.widget():
                child.widget().deleteLater()

        for i, grafico in enumerate(graficos):
            checkbox = QCheckBox(grafico["titulo"])
            checkbox.setChecked(True)

            checkbox.clicked.connect(self._verificar_estado_checkbox_todos)

            self.checkboxes_graficos[grafico["titulo"]] = {
                'checkbox': checkbox,
                'grafico_data': grafico
            }

            self.checkboxes_layout.addWidget(checkbox)

        self._verificar_estado_checkbox_todos()

    def _alternar_todos_checkboxes(self):
        if self.checkbox_todos.checkState() == Qt.PartiallyChecked:
            self.checkbox_todos.setCheckState(Qt.Checked)

        checked = self.checkbox_todos.checkState() == Qt.Checked

        logger.debug(f"Checkbox 'Selecionar Todos' foi {'marcado' if checked else 'desmarcado'}")

        self.checkbox_todos.blockSignals(True)

        for titulo, data in self.checkboxes_graficos.items():
            checkbox = data['checkbox']
            checkbox.blockSignals(True)
            checkbox.setChecked(checked)
            checkbox.blockSignals(False)
            logger.debug(f"Checkbox '{titulo}' definido como: {checked}")

        self.checkbox_todos.blockSignals(False)

    def _verificar_estado_checkbox_todos(self):
        if not self.checkboxes_graficos:
            return

        self.checkbox_todos.blockSignals(True)

        total_checkboxes = len(self.checkboxes_graficos)
        checkboxes_marcados = sum(1 for data in self.checkboxes_graficos.values() if data['checkbox'].isChecked())

        logger.debug(f"Verificando estado: {checkboxes_marcados}/{total_checkboxes} checkboxes marcados")

        if checkboxes_marcados == 0:
            self.checkbox_todos.setCheckState(Qt.Unchecked)

        elif checkboxes_marcados == total_checkboxes:
            self.checkbox_todos.setCheckState(Qt.Checked)

        else:
            self.checkbox_todos.setCheckState(Qt.PartiallyChecked)

        self.checkbox_todos.blockSignals(False)

    def _ajustar_largura_painel_selecao(self):
        if not self.painel_selecao or not self.gerador_atual:
            logger.debug("Painel de seleção ou gerador não disponíveis para ajuste de largura")
            return

        try:
            graficos = self._criar_lista_graficos(self.gerador_atual)

            nova_largura = self._calcular_largura_ideal(graficos)
            logger.debug(f"Nova largura calculada para o painel após mudança de idioma: {nova_largura}")

            self.painel_selecao.setMaximumWidth(nova_largura)
            self._atualizar_textos_checkboxes(graficos)

            if self.splitter:
                tamanhos = self.splitter.sizes()
                total = sum(tamanhos)
                proporcao = nova_largura / total * 100
                novo_tamanho_grafico = total - nova_largura
                self.splitter.setSizes([nova_largura, novo_tamanho_grafico])
                logger.debug(f"Ajustada largura do splitter: {nova_largura}/{novo_tamanho_grafico}")

        except Exception as e:
            logger.error(f"Erro ao ajustar largura do painel: {e}", exc_info=True)

    def _calcular_largura_ideal(self, graficos):

        font = QFont()
        font_metrics = QFontMetrics(font)

        max_text_width = 0
        for grafico in graficos:
            text_width = font_metrics.horizontalAdvance(grafico["titulo"])
            max_text_width = max(max_text_width, text_width)

        botoes_textos = [
            self.loc.get_text("save_selected") if "save_selected" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Salvar Selecionados",
            self.loc.get_text("save_all"),
            self.loc.get_text("refresh"),
            self.loc.get_text("select_all") if "select_all" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Selecionar Todos"
        ]

        for texto in botoes_textos:
            text_width = font_metrics.horizontalAdvance(texto)
            max_text_width = max(max_text_width, text_width)

        checkbox_padding = 40
        scroll_padding = 30 
        min_panel_width = max_text_width + checkbox_padding + scroll_padding

        max_width = max(min_panel_width, 200)
        max_width = min(max_width, 400)

        return max_width

    def _atualizar_textos_checkboxes(self, graficos):
        if not self.checkboxes_graficos:
            return

        if hasattr(self, 'checkbox_todos'):
            self.checkbox_todos.setText(self.loc.get_text("select_all") if "select_all" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Selecionar Todos")

        titulo_mapeamento = {}
        for grafico in graficos:
            for titulo_antigo, data in self.checkboxes_graficos.items():
                if data['grafico_data']['func'] == grafico['func']:
                    titulo_mapeamento[titulo_antigo] = grafico['titulo']
                    break

        for titulo_antigo, novo_titulo in titulo_mapeamento.items():
            if titulo_antigo in self.checkboxes_graficos:
                self.checkboxes_graficos[titulo_antigo]['checkbox'].setText(novo_titulo)

    def _gerar_todos_graficos(self, graficos):
        self.graficos_dados.clear()
        for grafico in graficos:
            try:
                logger.debug(f"Gerando gráfico: {grafico['titulo']}")
                fig = grafico["func"]()

                self.graficos_dados[grafico["titulo"]] = {
                    'fig': fig,
                    'func': grafico["func"],
                    'titulo': grafico["titulo"]
                }

                canvas = FigureCanvas(fig)
                tab = QWidget()
                tab_layout = QVBoxLayout()
                tab_layout.addWidget(canvas)
                tab.setLayout(tab_layout)
                self.tab_widget.addTab(tab, grafico["titulo"])

            except Exception as e:
                logger.error(f"Erro ao gerar gráfico {grafico['titulo']}: {e}", exc_info=True)

    def _atualizar_graficos(self, dialog_atual):
        try:
            if dialog_atual and dialog_atual.isVisible():
                dialog_atual.close()

            self.mostrar_estatisticas()

        except Exception as e:
            logger.error(f"Erro ao atualizar gráficos: {e}", exc_info=True)
            QMessageBox.critical(self.interface, self.loc.get_text("error"), self.loc.get_text("stats_error").format(str(e)))

    def _salvar_graficos_selecionados(self):
        try:
            graficos_selecionados = []
            for titulo, data in self.checkboxes_graficos.items():
                if data['checkbox'].isChecked():
                    if titulo in self.graficos_dados:
                        graficos_selecionados.append({
                            'titulo': titulo,
                            'fig': self.graficos_dados[titulo]['fig']
                        })

            if not graficos_selecionados:
                QMessageBox.warning(
                    self.interface, 
                    self.loc.get_text("warning"), 
                    self.loc.get_text("no_graphs_selected") if "no_graphs_selected" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Nenhum gráfico selecionado"
                )
                return

            logger.info(f"Iniciando salvamento de {len(graficos_selecionados)} gráficos selecionados")

            diretorio = QFileDialog.getExistingDirectory(
                self.interface, 
                self.loc.get_text("select_save_dir"), 
                "", 
                QFileDialog.ShowDirsOnly
            )

            if not diretorio:
                logger.debug("Operação de salvamento cancelada pelo usuário")
                return

            QApplication.setOverrideCursor(Qt.WaitCursor)

            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                estatisticas_texto = self.loc.get_text("statistics").replace(":", "").strip()
                selecionados_texto = self.loc.get_text("selected") if "selected" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Selecionados"
                diretorio_graficos = os.path.join(diretorio, f"{estatisticas_texto}_{selecionados_texto}_{timestamp}")
                os.makedirs(diretorio_graficos, exist_ok=True)

                resultados = {}
                graficos_salvos = 0

                for grafico in graficos_selecionados:
                    try:
                        arquivo_destino = os.path.join(diretorio_graficos, f"{grafico['titulo']}.png")
                        logger.debug(f"Salvando {grafico['titulo']} em {arquivo_destino}")

                        grafico['fig'].savefig(arquivo_destino, bbox_inches='tight', dpi=600)
                        logger.info(f"Gráfico {grafico['titulo']} salvo com sucesso")
                        resultados[grafico['titulo']] = True
                        graficos_salvos += 1

                    except Exception as e:
                        logger.error(f"Erro ao salvar {grafico['titulo']}: {e}", exc_info=True)
                        resultados[grafico['titulo']] = False

                QApplication.restoreOverrideCursor()

                detalhes = []
                for nome, sucesso in resultados.items():
                    status = self.loc.get_text("success") if sucesso else self.loc.get_text("failure")
                    detalhes.append(f"- {nome}: {status}")

                msg = QMessageBox(self.interface)
                msg.setWindowTitle(self.loc.get_text("graphs_saved"))
                msg.setIcon(QMessageBox.Information)

                msg_texto = self.loc.get_text("selected_graphs_saved_detail") if "selected_graphs_saved_detail" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Gráficos selecionados salvos: {}/{} em {}"
                msg.setText(msg_texto.format(graficos_salvos, len(graficos_selecionados), diretorio_graficos))
                msg.setDetailedText("\n".join(detalhes))
                msg.addButton(self.loc.get_text("ok"), QMessageBox.AcceptRole)
                btn_open = msg.addButton(self.loc.get_text("open_folder"), QMessageBox.ActionRole)

                self._traduzir_botoes_detalhes(msg)

                timer = QTimer(self.interface)
                timer.timeout.connect(lambda: self._traduzir_botoes_detalhes(msg))
                timer.start(10)

                msg.finished.connect(timer.stop)
                msg.exec()

                if msg.clickedButton() == btn_open:
                    self._abrir_diretorio(diretorio_graficos)

                logger.info(f"Gráficos selecionados salvos com sucesso: {graficos_salvos}/{len(graficos_selecionados)}")

            finally:
                QApplication.restoreOverrideCursor()

        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Erro ao salvar gráficos selecionados: {e}", exc_info=True)
            QMessageBox.critical(
                self.interface, 
                self.loc.get_text("error"), 
                self.loc.get_text("save_graphs_error").format(str(e))
            )

    def _abrir_diretorio(self, caminho):
        try:
            if sys.platform == 'win32':
                os.startfile(caminho)

            elif sys.platform == 'darwin':
                subprocess.call(['open', caminho])

            else:
                subprocess.call(['xdg-open', caminho])

        except Exception as e:
            logger.error(f"Erro ao abrir diretório: {e}", exc_info=True)

    def _traduzir_botoes_detalhes(self, msg):
        for botao in msg.buttons():
            if botao.text() == "Show Details..." or botao.text() == "Hide Details...":
                if "Hide" in botao.text():
                    botao.setText(self.loc.get_text("hide_details"))

                else:
                    botao.setText(self.loc.get_text("show_details"))

                fonte_metrica = botao.fontMetrics()
                texto_largura = fonte_metrica.horizontalAdvance(botao.text())

                largura_minima = texto_largura + 20

                botao.setMinimumWidth(largura_minima)
                botao.adjustSize()
