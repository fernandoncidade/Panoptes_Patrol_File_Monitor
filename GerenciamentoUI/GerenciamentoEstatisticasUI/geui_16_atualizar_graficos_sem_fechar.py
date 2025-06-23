from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _atualizar_graficos_sem_fechar(self):
    try:
        if not self.dialog_estatisticas or not self.dialog_estatisticas.isVisible():
            return

        self.dialog_estatisticas.setWindowTitle(self.loc.get_text("statistics"))

        if self.gerador_atual and self.tab_widget:
            self.gerador_atual.atualizar_textos_traduzidos()

            graficos_atualizados = self._criar_lista_graficos(self.gerador_atual)
            estados_checkboxes = self._obter_estados_checkboxes()
            mapeamento_funcoes = self._criar_mapeamento_funcoes(graficos_atualizados)

            self._regenerar_graficos_existentes(graficos_atualizados, mapeamento_funcoes)
            self._atualizar_checkboxes_graficos(graficos_atualizados, estados_checkboxes, mapeamento_funcoes)

        logger.info("Gráficos atualizados com sucesso sem fechar a janela")

    except Exception as e:
        logger.error(f"Erro ao atualizar gráficos sem fechar: {e}", exc_info=True)
