def _atualizar_interface_apos_evento(self, evento):
    try:
        interface = None
        if self.callback and hasattr(self.callback, '__self__'):
            interface = self.callback.__self__

        elif hasattr(self.observador, 'interface'):
            interface = self.observador.interface

        if interface and hasattr(interface, 'gerenciador_tabela'):
            interface.gerenciador_tabela.atualizar_linha_mais_recente(interface.tabela_dados)

            from Observador.ob_08_EventoMovido import _atualizar_contador_eventos
            _atualizar_contador_eventos(interface)

            interface.atualizar_status()

    except Exception as e:
        print(f"Erro ao atualizar interface após evento: {e}")
