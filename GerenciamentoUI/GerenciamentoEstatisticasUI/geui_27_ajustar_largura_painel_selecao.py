from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _ajustar_largura_painel_selecao(self):
    if not self.painel_selecao or not self.gerador_atual:
        logger.debug("Painel de seleção ou gerador não disponíveis para ajuste de largura")
        return

    try:
        graficos = self._criar_lista_graficos(self.gerador_atual)
        largura_botao = 25

        nova_largura = self._calcular_largura_ideal(graficos)
        logger.debug(f"Nova largura calculada para o painel após mudança de idioma: {nova_largura}")

        if hasattr(self, 'painel_selecao_interno') and not self.painel_recolhido:
            self.painel_selecao_interno.setFixedWidth(nova_largura)
            largura_total = largura_botao + nova_largura
            self.painel_selecao.setFixedWidth(largura_total)

        self.tamanho_painel_original = nova_largura
        self._atualizar_textos_checkboxes(graficos)

        if self.splitter and not self.painel_recolhido:
            tamanhos = self.splitter.sizes()
            total = sum(tamanhos)
            nova_largura_graficos = total - self.painel_selecao.width()
            self.splitter.setSizes([self.painel_selecao.width(), nova_largura_graficos])
            logger.debug(f"Ajustada largura do splitter: {self.painel_selecao.width()}/{nova_largura_graficos}")

    except Exception as e:
        logger.error(f"Erro ao ajustar largura do painel: {e}", exc_info=True)
