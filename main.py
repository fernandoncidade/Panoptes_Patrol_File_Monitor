import sys
from PySide6.QtWidgets import QApplication
from InterfaceCore.ic_01_InterfaceMonitor import InterfaceMonitor, Internacionalizador
from GerenciamentoUI.ui_12_Localizador import Localizador
from utils.LogManager import LogManager

logger = LogManager.get_logger()

if __name__ == '__main__':
    try:
        logger.info("=== Iniciando aplicação Panoptes_Patrol ===")
        app = QApplication(sys.argv)

        loc_temp = Localizador()
        idioma = loc_temp.idioma_atual

        Internacionalizador.inicializar_tradutor_qt(app, idioma)

        logger.info(f"Traduções do Qt carregadas para o idioma: {idioma}")

        window = InterfaceMonitor()
        window.show()
        logger.info("Janela principal exibida, iniciando loop de eventos")
        exit_code = app.exec()
        logger.info(f"Aplicação encerrada com código de saída: {exit_code}")
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Erro fatal ao iniciar aplicação: {e}", exc_info=True)
        sys.exit(1)
