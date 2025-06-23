def _traduzir_botoes_detalhes(self, msg):
    for botao in msg.buttons():
        if botao.text() == "Show Details..." or botao.text() == "Hide Details...":
            if "Hide" in botao.text():
                botao.setText(self.loc.get_text("hide_details"))

            else:
                botao.setText(self.loc.get_text("show_details"))

            fonte_metrica = botao.fontMetrics()
            texto_largura = fonte_metrica.horizontalAdvance(botao.text())

            largura_minima = texto_largura + 20

            botao.setMinimumWidth(largura_minima)
            botao.adjustSize()
