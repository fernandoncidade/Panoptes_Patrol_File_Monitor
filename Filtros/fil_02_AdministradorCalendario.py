from PySide6.QtWidgets import QCalendarWidget
from PySide6.QtCore import Qt, QDateTime


class AdministradorCalendario:
    def __init__(self, parent):
        self.parent = parent
        
    def mostrar_calendario(self, campo_data):
        calendario = QCalendarWidget(self.parent)
        calendario.setWindowFlags(Qt.Popup)
        calendario.clicked.connect(lambda date: self.selecionar_data(date, campo_data, calendario))
        
        pos = campo_data.mapToGlobal(campo_data.rect().bottomLeft())
        calendario.move(pos)
        calendario.show()

    def selecionar_data(self, data, campo_data, calendario):
        dt = QDateTime(data, campo_data.dateTime().time())
        campo_data.setDateTime(dt)
        calendario.close()
        self.parent.administrador_filtros.aplicar_filtros()
