from .ob_02_BaseEvento import BaseEvento


class EventoAdicionado(BaseEvento):
    def processar(self, nome_arquivo, caminho_completo, tempo_atual):
        if nome_arquivo in self.observador.registros_anteriores:
            return False
        
        self.observador.arquivos_recem_adicionados[nome_arquivo] = tempo_atual
        self.notificar_evento(self.observador.loc.get_text("op_added"), nome_arquivo, "", caminho_completo)
        return True
