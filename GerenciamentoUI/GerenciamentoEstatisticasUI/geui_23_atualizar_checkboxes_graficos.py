from PySide6.QtWidgets import QCheckBox
from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _atualizar_checkboxes_graficos(self, graficos_atualizados, estados_checkboxes, mapeamento_funcoes):
    try:
        while self.checkboxes_layout.count() > 2:
            child = self.checkboxes_layout.takeAt(2)
            if child.widget():
                child.widget().deleteLater()

        self.checkboxes_graficos.clear()

        for grafico in graficos_atualizados:
            checkbox = QCheckBox(grafico["titulo"])
            checkbox_checked = estados_checkboxes.get(grafico['func'], True)
            checkbox.setChecked(checkbox_checked)
            checkbox.clicked.connect(self._verificar_estado_checkbox_todos)
            self.checkboxes_graficos[grafico["titulo"]] = {'checkbox': checkbox, 'grafico_data': grafico}
            self.checkboxes_layout.addWidget(checkbox)

        self._verificar_estado_checkbox_todos()

    except Exception as e:
        logger.error(f"Erro ao atualizar checkboxes: {e}", exc_info=True)
