import os
import subprocess
from datetime import datetime
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox
from utils.LogManager import LogManager

logger = LogManager.get_logger()

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

        diretorio = QFileDialog.getExistingDirectory(self.interface, self.loc.get_text("select_save_dir"), "", QFileDialog.ShowDirsOnly)

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
