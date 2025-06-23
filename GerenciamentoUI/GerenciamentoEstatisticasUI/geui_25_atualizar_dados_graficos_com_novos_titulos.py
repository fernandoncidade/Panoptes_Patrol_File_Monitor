from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _atualizar_dados_graficos_com_novos_titulos(self, graficos_atualizados, mapeamento_funcoes):
    try:
        novos_dados = {}

        for titulo_antigo, dados in self.graficos_dados.items():
            func = dados['func']
            if func in mapeamento_funcoes:
                novo_titulo = mapeamento_funcoes[func]
                novos_dados[novo_titulo] = {'fig': dados['fig'], 'func': func, 'titulo': novo_titulo}

            else:
                novos_dados[titulo_antigo] = dados

        self.graficos_dados = novos_dados

    except Exception as e:
        logger.error(f"Erro ao atualizar dados dos gráficos: {e}", exc_info=True)
