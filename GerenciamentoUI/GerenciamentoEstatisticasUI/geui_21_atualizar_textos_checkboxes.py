from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _atualizar_textos_checkboxes(self, graficos):
    if not self.checkboxes_graficos:
        return

    if hasattr(self, 'checkbox_todos'):
        self.checkbox_todos.setText(self.loc.get_text("select_all") if "select_all" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Selecionar Todos")

    titulo_mapeamento = {}
    for grafico in graficos:
        for titulo_antigo, data in self.checkboxes_graficos.items():
            if data['grafico_data']['func'] == grafico['func']:
                titulo_mapeamento[titulo_antigo] = grafico['titulo']
                break

    for titulo_antigo, novo_titulo in titulo_mapeamento.items():
        if titulo_antigo in self.checkboxes_graficos:
            self.checkboxes_graficos[titulo_antigo]['checkbox'].setText(novo_titulo)
