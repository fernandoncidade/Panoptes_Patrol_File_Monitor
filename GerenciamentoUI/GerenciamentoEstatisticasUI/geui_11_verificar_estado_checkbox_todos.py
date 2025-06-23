from PySide6.QtCore import Qt
from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _verificar_estado_checkbox_todos(self):
    if not self.checkboxes_graficos:
        return

    self.checkbox_todos.blockSignals(True)

    total_checkboxes = len(self.checkboxes_graficos)
    checkboxes_marcados = sum(1 for data in self.checkboxes_graficos.values() if data['checkbox'].isChecked())

    logger.debug(f"Verificando estado: {checkboxes_marcados}/{total_checkboxes} checkboxes marcados")

    if checkboxes_marcados == 0:
        self.checkbox_todos.setCheckState(Qt.Unchecked)

    elif checkboxes_marcados == total_checkboxes:
        self.checkbox_todos.setCheckState(Qt.Checked)

    else:
        self.checkbox_todos.setCheckState(Qt.PartiallyChecked)

    self.checkbox_todos.blockSignals(False)
