from PySide6.QtCore import Qt
from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _alternar_todos_checkboxes(self):
    if self.checkbox_todos.checkState() == Qt.PartiallyChecked:
        self.checkbox_todos.setCheckState(Qt.Checked)

    checked = self.checkbox_todos.checkState() == Qt.Checked

    logger.debug(f"Checkbox 'Selecionar Todos' foi {'marcado' if checked else 'desmarcado'}")

    self.checkbox_todos.blockSignals(True)

    for titulo, data in self.checkboxes_graficos.items():
        checkbox = data['checkbox']
        checkbox.blockSignals(True)
        checkbox.setChecked(checked)
        checkbox.blockSignals(False)
        logger.debug(f"Checkbox '{titulo}' definido como: {checked}")

    self.checkbox_todos.blockSignals(False)
