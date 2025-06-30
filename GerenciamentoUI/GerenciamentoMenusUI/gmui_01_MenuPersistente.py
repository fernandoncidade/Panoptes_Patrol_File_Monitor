from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Qt


class MenuPersistente(QMenu):
    def __init__(self, titulo, parent=None):
        super().__init__(titulo, parent)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        action = self.actionAt(event.pos())
        if action and action.isEnabled():
            if not action.menu():
                action.trigger()
                event.accept()
                return

        super().mousePressEvent(event)

    def leaveEvent(self, event):
        pos = self.mapFromGlobal(self.parent().cursor().pos())
        if not self.rect().contains(pos):
            self.close()

        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        action = self.actionAt(event.pos())
        if action and action.isEnabled() and not action.menu():
            event.accept()
            return

        super().mouseReleaseEvent(event)
