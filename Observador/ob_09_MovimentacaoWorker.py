import threading
from PySide6.QtCore import QObject, Signal


class MovimentacaoWorker(QObject):
    processamento_concluido = Signal()
    atualizacao_progresso = Signal(int, int)

    def __init__(self, interface, parent=None):
        super().__init__(parent)
        self.interface = interface
        self.evento_base = interface.evento_base
        self.mutex = threading.Lock()
        self.processando = False
        self.eventos_pendentes = []

    def adicionar_evento(self, evento):
        with self.mutex:
            self.eventos_pendentes.append(evento)

    def processar_eventos(self):
        if self.processando:
            return

        with self.mutex:
            if not self.eventos_pendentes:
                return

            eventos = self.eventos_pendentes.copy()
            self.eventos_pendentes = []
            self.processando = True

        threading.Thread(target=self._processar_lote, args=(eventos,), daemon=True).start()

    def _processar_lote(self, eventos):
        try:
            if eventos:
                self.atualizacao_progresso.emit(0, len(eventos))
                def after_process():
                    self.processamento_concluido.emit()
                    if hasattr(self.interface, 'gerenciador_tabela'):
                        self.interface.gerenciador_tabela.atualizacao_pendente = True

                self.evento_base.processar_eventos_movimentacao(eventos, after_process)

        finally:
            with self.mutex:
                self.processando = False
