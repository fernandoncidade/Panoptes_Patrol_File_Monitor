def _finalizar_scan(self):
    if hasattr(self.observador, 'interface') and hasattr(self.observador.interface, 'barra_progresso'):
        self.observador.interface.barra_progresso.hide()
        self.observador.interface.barra_progresso.setValue(0)

        if hasattr(self.observador.interface, 'gerenciador_tabela'):
            self.observador.interface.gerenciador_tabela.atualizar_dados_tabela(self.observador.interface.tabela_dados)

            from Observador.ob_08_EventoMovido import _atualizar_contador_eventos
            _atualizar_contador_eventos(self.observador.interface)
            self.observador.interface.atualizar_status()
