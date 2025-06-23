from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _atualizar_abas_graficos(self, graficos_atualizados, mapeamento_funcoes):
    try:
        if not self.tab_widget:
            return

        funcoes_para_indices = {}

        for i in range(self.tab_widget.count()):
            titulo_atual = self.tab_widget.tabText(i)

            for titulo_antigo, data in self.checkboxes_graficos.items():
                if titulo_antigo == titulo_atual:
                    funcoes_para_indices[data['grafico_data']['func']] = i
                    break

        for func, indice in funcoes_para_indices.items():
            if func in mapeamento_funcoes:
                novo_titulo = mapeamento_funcoes[func]
                self.tab_widget.setTabText(indice, novo_titulo)

    except Exception as e:
        logger.error(f"Erro ao atualizar abas dos gráficos: {e}", exc_info=True)
