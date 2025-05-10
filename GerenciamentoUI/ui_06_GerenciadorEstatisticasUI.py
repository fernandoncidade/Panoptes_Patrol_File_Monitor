import os
import sys
import logging
import sqlite3
import subprocess
from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QTabWidget, QWidget, QPushButton,
                               QMessageBox, QFileDialog, QApplication)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

logger = logging.getLogger('FileManager')


class GerenciadorEstatisticasUI:
    def __init__(self, interface_principal):
        self.interface = interface_principal
        self.loc = interface_principal.loc
        self.evento_base = interface_principal.evento_base
        self.dialog_estatisticas = None

        if hasattr(self.loc, 'idioma_alterado'):
            self.loc.idioma_alterado.connect(self.atualizar_graficos_apos_mudanca_idioma)

    def atualizar_graficos_apos_mudanca_idioma(self, novo_idioma):
        if self.dialog_estatisticas and self.dialog_estatisticas.isVisible():
            self._atualizar_graficos(self.dialog_estatisticas)

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
                logger.error(f"Erro ao verificar quantidade de dados: {e}")
                QMessageBox.critical(self.interface, self.loc.get_text("error"), 
                                     f"{self.loc.get_text('stats_error')}: {str(e)}")
                return

            self.dialog_estatisticas = QDialog(None)  

            self.dialog_estatisticas.setWindowFlags(
                Qt.Window |                   # Janela independente
                Qt.WindowSystemMenuHint |     # Menu de sistema 
                Qt.WindowMinMaxButtonsHint |  # Botões maximizar/minimizar
                Qt.WindowCloseButtonHint      # Botão fechar
            )

            self.dialog_estatisticas.finished.connect(self.limpar_referencia_dialog)

            estatisticas_icon = QIcon(os.path.join(icon_path, "statistics.ico"))
            self.dialog_estatisticas.setWindowIcon(estatisticas_icon)
            self.dialog_estatisticas.setWindowTitle(self.loc.get_text("statistics"))
            self.dialog_estatisticas.setMinimumSize(800, 600)
            layout = QVBoxLayout()
            tab_widget = QTabWidget()

            from Estatistica.st_01_GeradorEstatisticas import GeradorEstatisticas

            self.gerador_atual = GeradorEstatisticas(self.evento_base.db_path, self.loc, self.interface)
            gerador = self.gerador_atual

            QApplication.setOverrideCursor(Qt.WaitCursor)

            try:
                logger.debug("Obtendo dados para estatísticas")
                df = gerador._obter_dados()

                if df.empty:
                    logger.warning("DataFrame vazio, não é possível gerar gráficos")
                    QApplication.restoreOverrideCursor()
                    QMessageBox.warning(self.interface, self.loc.get_text("warning"), self.loc.get_text("no_data_to_plot"))
                    return

                graficos = self._criar_lista_graficos(gerador)

                for grafico in graficos:
                    try:
                        logger.debug(f"Gerando gráfico: {grafico['titulo']}")
                        fig = grafico["func"]()
                        canvas = FigureCanvas(fig)
                        tab = QWidget()
                        tab_layout = QVBoxLayout()
                        tab_layout.addWidget(canvas)
                        tab.setLayout(tab_layout)
                        tab_widget.addTab(tab, grafico["titulo"])

                    except Exception as e:
                        logger.error(f"Erro ao gerar gráfico {grafico['titulo']}: {e}", exc_info=True)

                if tab_widget.count() == 0:
                    raise Exception(self.loc.get_text("all_graphs_failed"))

                layout.addWidget(tab_widget)

                button_layout = QHBoxLayout()

                btn_salvar = QPushButton(self.loc.get_text("save_all"))
                btn_salvar.setIcon(QIcon(os.path.join(icon_path, "salvar.ico")))
                btn_salvar.clicked.connect(lambda: self.salvar_todos_graficos(gerador))

                btn_atualizar = QPushButton(self.loc.get_text("refresh"))
                btn_atualizar.setIcon(QIcon(os.path.join(icon_path, "atualizar.ico")))
                btn_atualizar.clicked.connect(lambda: self._atualizar_graficos(self.dialog_estatisticas))

                button_layout.addStretch()
                button_layout.addWidget(btn_atualizar)
                button_layout.addWidget(btn_salvar)

                layout.addLayout(button_layout)
                self.dialog_estatisticas.setLayout(layout)

                logger.info("Dialog de estatísticas criado com sucesso")

            finally:
                QApplication.restoreOverrideCursor()

            self.dialog_estatisticas.show()

        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Erro ao mostrar estatísticas: {e}", exc_info=True)
            QMessageBox.critical(self.interface, self.loc.get_text("error"), self.loc.get_text("stats_error").format(str(e)))

    def limpar_referencia_dialog(self):
        self.dialog_estatisticas = None

    def _atualizar_graficos(self, dialog_atual):
        try:
            if dialog_atual and dialog_atual.isVisible():
                dialog_atual.close()

            self.mostrar_estatisticas()

        except Exception as e:
            logger.error(f"Erro ao atualizar gráficos: {e}", exc_info=True)
            QMessageBox.critical(self.interface, self.loc.get_text("error"), self.loc.get_text("stats_error").format(str(e)))

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
             "func": gerador.grafico_cluster_linha}
        ]

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

                resultados = gerador.salvar_graficos(diretorio_graficos)

                QApplication.restoreOverrideCursor()

                detalhes = []
                graficos_ok = 0
                for nome, sucesso in resultados.items():
                    status = self.loc.get_text("success") if sucesso else self.loc.get_text("failure")
                    detalhes.append(f"- {nome}: {status}")
                    if sucesso:
                        graficos_ok += 1

                msg = QMessageBox(self.interface)
                msg.setWindowTitle(self.loc.get_text("graphs_saved"))
                msg.setIcon(QMessageBox.Information)
                msg.setText(self.loc.get_text("graphs_saved_detail").format(graficos_ok, len(resultados), diretorio_graficos))
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

                logger.info(f"Gráficos salvos com sucesso: {graficos_ok}/{len(resultados)}")

            finally:
                QApplication.restoreOverrideCursor()

        except Exception as e:
            QApplication.restoreOverrideCursor()
            logger.error(f"Erro ao salvar gráficos: {e}", exc_info=True)
            QMessageBox.critical(self.interface, self.loc.get_text("error"), self.loc.get_text("save_graphs_error").format(str(e)))

    def _abrir_diretorio(self, caminho):
        try:
            if sys.platform == 'win32':
                os.startfile(caminho)

            elif sys.platform == 'darwin':
                subprocess.call(['open', caminho])

            else:
                subprocess.call(['xdg-open', caminho])

        except Exception as e:
            logger.error(f"Erro ao abrir diretório: {e}")

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
