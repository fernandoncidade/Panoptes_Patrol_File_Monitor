def _obter_estados_checkboxes(self):
    estados = {}
    for titulo, data in self.checkboxes_graficos.items():
        estados[data['grafico_data']['func']] = data['checkbox'].isChecked()

    return estados
