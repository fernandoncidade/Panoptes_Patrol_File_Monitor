import os

def notificar_evento(self, tipo_operacao, nome, dir_anterior, dir_atual):
    if not self.observador.ativo or self.observador.desligando:
        return

    nome_base = os.path.basename(nome)

    try:
        print(f"Notificando evento: {tipo_operacao} - {nome_base}")
        print(f"  Dir anterior: {dir_anterior}")
        print(f"  Dir atual: {dir_atual}")

        if tipo_operacao == self.observador.loc.get_text("op_deleted"):
            evento = self._criar_evento_exclusao(nome_base, dir_anterior)

            if evento and hasattr(self.observador, 'interface'):
                from Observador.ob_08_EventoMovido import verificar_movimentacao
                evento_processado = verificar_movimentacao(self.observador.interface, evento)

                if evento_processado is None:
                    caminho_completo = os.path.join(dir_anterior, nome_base)

                    arquivo_existe_em_outro_lugar = False
                    if hasattr(self.observador, 'interface') and hasattr(self.observador.interface, 'diretorio_atual'):
                        dir_monitorado = self.observador.interface.diretorio_atual
                        for raiz, dirs, arquivos in os.walk(dir_monitorado):
                            if nome_base in arquivos or nome_base in dirs:
                                arquivo_existe_em_outro_lugar = True
                                break

                    if not arquivo_existe_em_outro_lugar and not os.path.exists(caminho_completo):
                        evento["_temporario"] = False
                        self.processar_exclusao(evento)
                        return

                    else:
                        evento["_temporario"] = True
                        self.processar_exclusao(evento)
                        return

                evento = evento_processado

        else:
            evento = self._criar_evento_padrao(tipo_operacao, nome_base, dir_anterior, dir_atual)

            if evento and hasattr(self.observador, 'interface'):
                from Observador.ob_08_EventoMovido import verificar_movimentacao
                evento_processado = verificar_movimentacao(self.observador.interface, evento)

                if evento_processado and evento_processado["tipo_operacao"] == self.observador.loc.get_text("op_moved"):
                    self._remover_exclusao_temporaria(evento_processado["nome"], evento_processado["dir_anterior"])

                if evento_processado is None:
                    return
                
                evento = evento_processado

        if evento:
            self.registrar_evento_no_banco(evento)

    except Exception as e:
        print(f"Erro ao notificar evento: {e}")
        import traceback
        traceback.print_exc()
