from PySide6.QtCore import QMetaObject, Qt, Q_ARG

def _atualizar_interface(self, progresso, contador, total):
    try:
        if not hasattr(self.observador, 'interface'):
            return

        QMetaObject.invokeMethod(self.observador.interface,
                                 "atualizar_progresso_scan",
                                 Qt.ConnectionType.QueuedConnection,
                                 Q_ARG(int, progresso),
                                 Q_ARG(int, contador),
                                 Q_ARG(int, total))

    except Exception as e:
        print(f"Erro ao atualizar interface: {e}")
