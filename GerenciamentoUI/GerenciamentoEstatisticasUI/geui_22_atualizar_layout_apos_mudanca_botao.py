from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _atualizar_layout_apos_mudanca_botao(self):
    if not hasattr(self, 'painel_selecao_interno') or not self.btn_toggle_painel:
        return

    try:
        nova_largura_botao = self.btn_toggle_painel.width()

        if not self.painel_recolhido:
            largura_total = nova_largura_botao + self.tamanho_painel_original
            self.painel_selecao.setFixedWidth(largura_total)

        else:
            self.painel_selecao.setFixedWidth(nova_largura_botao)

        if self.splitter:
            tamanhos = self.splitter.sizes()
            total_largura = sum(tamanhos)
            nova_largura_graficos = total_largura - self.painel_selecao.width()
            self.splitter.setSizes([self.painel_selecao.width(), nova_largura_graficos])

    except Exception as e:
        logger.error(f"Erro ao atualizar layout após mudança do botão: {e}", exc_info=True)
