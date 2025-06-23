from PySide6.QtWidgets import QMessageBox
from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _atualizar_graficos(self, dialog_atual):
    try:
        self._atualizar_graficos_sem_fechar()

    except Exception as e:
        logger.error(f"Erro ao atualizar gráficos: {e}", exc_info=True)
        QMessageBox.critical(self.interface, self.loc.get_text("error"), self.loc.get_text("stats_error").format(str(e)))
