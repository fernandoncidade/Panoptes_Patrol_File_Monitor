import os
import subprocess
from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from utils.LogManager import LogManager

logger = LogManager.get_logger()

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
