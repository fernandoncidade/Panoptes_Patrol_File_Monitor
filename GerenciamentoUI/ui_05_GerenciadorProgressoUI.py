from utils.LogManager import LogManager
from datetime import datetime
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

logger = LogManager.get_logger()


class GerenciadorProgressoUI:
    def __init__(self, interface_principal):
        self.interface = interface_principal
        self.loc = interface_principal.loc

    def criar_barra_progresso(self):
        try:
            logger.debug("Criando/configurando barra de progresso")
            if hasattr(self.interface, 'barra_progresso'):
                self.interface.barra_progresso.setValue(0)
                self.interface.barra_progresso.setFormat("%p%")
                self.interface.barra_progresso.setTextVisible(True)
                self.interface.barra_progresso.show()
                self.interface.rotulo_resultado.setText(self.loc.get_text("preparing_scan"))
                logger.debug("Barra de progresso configurada e exibida")
                QApplication.processEvents()

        except Exception as e:
            logger.error(f"Erro ao criar barra de progresso: {e}", exc_info=True)

    def atualizar_progresso_scan(self, progresso, contador, total):
        try:
            if hasattr(self.interface, 'rotulo_resultado'):
                msg = f"{self.loc.get_text('scanning')} {progresso}% ({contador}/{total})"

                if total > 1000 and contador > 0 and progresso < 100:
                    if not hasattr(self.interface, '_scan_start_time'):
                        self.interface._scan_start_time = datetime.now()

                    tempo_decorrido = (datetime.now() - self.interface._scan_start_time).total_seconds()
                    if progresso > 0:
                        tempo_estimado_total = tempo_decorrido * (100 / progresso)
                        tempo_restante = tempo_estimado_total - tempo_decorrido

                        minutos = int(tempo_restante // 60)
                        segundos = int(tempo_restante % 60)

                        if minutos > 0:
                            msg += f" - {self.loc.get_text('remaining')}: {minutos}m {segundos}s"

                        else:
                            msg += f" - {self.loc.get_text('remaining')}: {segundos}s"

                self.interface.rotulo_resultado.setText(msg)

            if hasattr(self.interface, 'barra_progresso'):
                if not self.interface.barra_progresso.isVisible():
                    self.interface.barra_progresso.show()

                self.interface.barra_progresso.setValue(progresso)

                if progresso >= 100:
                    QTimer.singleShot(1000, lambda: self.interface.barra_progresso.hide())

                    if hasattr(self.interface, '_scan_start_time'):
                        delattr(self.interface, '_scan_start_time')

                    self.interface.rotulo_resultado.setText(f"{self.loc.get_text('scan_complete')} ({total} {self.loc.get_text('items')})")

            QApplication.processEvents()

        except Exception as e:
            logger.error(f"Erro ao atualizar progresso: {e}", exc_info=True)
