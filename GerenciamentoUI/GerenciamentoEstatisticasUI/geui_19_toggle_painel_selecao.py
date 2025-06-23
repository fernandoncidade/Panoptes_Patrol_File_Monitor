from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _toggle_painel_selecao(self):
    if not hasattr(self, 'painel_selecao_interno'):
        return

    largura_botao = self.btn_toggle_painel.width()

    if self.painel_recolhido:
        self.painel_selecao_interno.setFixedWidth(self.tamanho_painel_original)
        self.painel_selecao_interno.setVisible(True)

        largura_total = largura_botao + self.tamanho_painel_original
        self.painel_selecao.setFixedWidth(largura_total)

        texto_ocultar = self.loc.get_text("hide_selection_panel") if "hide_selection_panel" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Ocultar Painel de Seleção"
        self.btn_toggle_painel.setText(texto_ocultar)

    else:
        self.painel_selecao_interno.setVisible(False)
        self.painel_selecao_interno.setFixedWidth(0)

        self.painel_selecao.setFixedWidth(largura_botao)

        texto_expandir = self.loc.get_text("expand_selection_panel") if "expand_selection_panel" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Expandir Painel de Seleção"
        self.btn_toggle_painel.setText(texto_expandir)

    self.painel_recolhido = not self.painel_recolhido

    if self.splitter:
        tamanhos = self.splitter.sizes()
        total_largura = sum(tamanhos)
        nova_largura_painel = self.painel_selecao.width()
        nova_largura_graficos = total_largura - nova_largura_painel

        self.splitter.setSizes([nova_largura_painel, nova_largura_graficos])
