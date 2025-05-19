import sqlite3

def _atualizar_interface_apos_exclusao(self):
    try:
        self.eventos_excluidos += 1

        interface = None
        if self.callback and hasattr(self.callback, '__self__'):
            interface = self.callback.__self__

        elif hasattr(self.observador, 'interface'):
            interface = self.observador.interface

        if interface and hasattr(interface, 'gerenciador_tabela'):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(id) FROM monitoramento WHERE tipo_operacao = ?", (self.observador.loc.get_text("op_deleted"),))
                result = cursor.fetchone()
                if result and result[0]:
                    ultimo_id_exclusao = result[0]
                    if not hasattr(self, '_ultimo_id_exclusao_exibido'):
                        self._ultimo_id_exclusao_exibido = 0

                    if self._ultimo_id_exclusao_exibido < ultimo_id_exclusao:
                        if ultimo_id_exclusao - self._ultimo_id_exclusao_exibido < 5:
                            for _ in range(ultimo_id_exclusao - self._ultimo_id_exclusao_exibido):
                                interface.gerenciador_tabela.atualizar_linha_mais_recente(interface.tabela_dados)

                        else:
                            interface.gerenciador_tabela.atualizar_dados_tabela(interface.tabela_dados)

                        self._ultimo_id_exclusao_exibido = ultimo_id_exclusao

            from Observador.ob_08_EventoMovido import _atualizar_contador_eventos
            _atualizar_contador_eventos(interface)

            interface.atualizar_status()

    except Exception as e:
        print(f"Erro ao atualizar interface após exclusão: {e}")
