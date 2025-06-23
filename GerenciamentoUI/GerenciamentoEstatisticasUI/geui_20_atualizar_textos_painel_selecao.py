from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _atualizar_textos_painel_selecao(self):
    try:
        if hasattr(self, 'titulo_selecionar_graficos'):
            self.titulo_selecionar_graficos.setText(
                self.loc.get_text("select_graphs") if "select_graphs" in self.loc.traducoes.get(self.loc.idioma_atual, {}) 
                else "Selecionar Gráficos"
            )

        if hasattr(self, 'checkbox_todos'):
            self.checkbox_todos.setText(
                self.loc.get_text("select_all") if "select_all" in self.loc.traducoes.get(self.loc.idioma_atual, {}) 
                else "Selecionar Todos"
            )

        if hasattr(self, 'btn_salvar_selecionados'):
            self.btn_salvar_selecionados.setText(
                self.loc.get_text("save_selected") if "save_selected" in self.loc.traducoes.get(self.loc.idioma_atual, {}) 
                else "Salvar Selecionados"
            )

        if hasattr(self, 'btn_salvar_todos'):
            self.btn_salvar_todos.setText(self.loc.get_text("save_all"))

        if hasattr(self, 'btn_atualizar'):
            self.btn_atualizar.setText(self.loc.get_text("refresh"))

    except Exception as e:
        logger.error(f"Erro ao atualizar textos do painel de seleção: {e}", exc_info=True)
