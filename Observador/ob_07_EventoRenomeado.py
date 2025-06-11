import time
from .ob_02_BaseEvento import BaseEvento


class EventoRenomeado(BaseEvento):
    def processar(self, nome_arquivo, caminho_completo, acao):
        if acao == 4:
            self.observador.registros_anteriores[nome_arquivo] = caminho_completo

        elif acao == 5 and self.observador.registros_anteriores:
            nome_antigo = next(iter(self.observador.registros_anteriores))
            dir_anterior = self.observador.registros_anteriores.pop(nome_antigo)

            tempo_atual = time.time()
            self.observador.arquivos_recem_renomeados[nome_arquivo] = tempo_atual
            self.observador.arquivos_recem_adicionados[nome_arquivo] = tempo_atual

            self.notificar_evento(self.observador.loc.get_text("op_renamed"), nome_arquivo, dir_anterior, caminho_completo)

        return True
