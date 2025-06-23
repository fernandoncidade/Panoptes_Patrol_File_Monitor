from PySide6.QtWidgets import QCheckBox
from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _popular_checkboxes(self, graficos):
    logger.debug(f"Populando {len(graficos)} checkboxes")

    self.checkboxes_graficos.clear()

    while self.checkboxes_layout.count() > 2:
        child = self.checkboxes_layout.takeAt(2)
        if child.widget():
            child.widget().deleteLater()

    for i, grafico in enumerate(graficos):
        checkbox = QCheckBox(grafico["titulo"])
        checkbox.setChecked(True)
        checkbox.clicked.connect(self._verificar_estado_checkbox_todos)
        self.checkboxes_graficos[grafico["titulo"]] = {'checkbox': checkbox, 'grafico_data': grafico}
        self.checkboxes_layout.addWidget(checkbox)

    self._verificar_estado_checkbox_todos()
