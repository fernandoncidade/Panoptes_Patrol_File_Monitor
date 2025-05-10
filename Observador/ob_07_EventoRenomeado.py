from .ob_02_BaseEvento import BaseEvento


class EventoRenomeado(BaseEvento):
    def processar(self, nome_arquivo, caminho_completo, acao):
        if acao == 4:
            self.observador.registros_anteriores[nome_arquivo] = caminho_completo

        elif acao == 5 and self.observador.registros_anteriores:
            nome_antigo = next(iter(self.observador.registros_anteriores))
            dir_anterior = self.observador.registros_anteriores.pop(nome_antigo)
            self.notificar_evento(self.observador.loc.get_text("op_renamed"), nome_arquivo, dir_anterior, caminho_completo)

        return True
