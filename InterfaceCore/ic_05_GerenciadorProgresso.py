from utils.LogManager import LogManager
from PySide6.QtCore import Slot, QTimer


class GerenciadorProgresso:
    @staticmethod
    @Slot()
    def criar_barra_progresso(interface):
        logger = LogManager.get_logger()
        logger.debug("Criando barra de progresso")
        interface.gerenciador_progresso_ui.criar_barra_progresso()

    @staticmethod
    @Slot(int, int, int)
    def atualizar_progresso_scan(interface, progresso, contador, total):
        logger = LogManager.get_logger()
        logger.debug(f"Atualizando progresso: {progresso}% ({contador}/{total})")
        interface.gerenciador_progresso_ui.atualizar_progresso_scan(progresso, contador, total)

    @staticmethod
    def esconder_barra_progresso(interface):
        logger = LogManager.get_logger()
        logger.debug("Escondendo barra de progresso")
        if hasattr(interface, 'barra_progresso'):
            QTimer.singleShot(1000, interface.barra_progresso.hide)
            interface.barra_progresso.setValue(0)
            logger.debug("Barra de progresso ocultada")
