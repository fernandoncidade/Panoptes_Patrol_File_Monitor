from .ob_02_BaseEvento import BaseEvento


class EventoExcluido(BaseEvento):
    def processar(self, nome_arquivo, caminho_completo, tempo_atual):
        self.observador.arquivos_recem_excluidos[nome_arquivo] = tempo_atual

        if nome_arquivo in self.observador.registros_anteriores:
            del self.observador.registros_anteriores[nome_arquivo]

        self.notificar_evento(self.observador.loc.get_text("op_deleted"), nome_arquivo, caminho_completo, "")
        return True
