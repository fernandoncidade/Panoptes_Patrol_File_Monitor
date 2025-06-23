from utils.LogManager import LogManager
from Observador.ob_08_EventoMovido import verificar_movimentacao, adicionar_evento

logger = LogManager.get_logger()


class GerenciadorEventosArquivo:
    def __init__(self, interface_principal):
        self.interface = interface_principal

    def verificar_movimentacao(self, evento):
        return verificar_movimentacao(self.interface, evento)

    def adicionar_evento(self, evento):
        adicionar_evento(self.interface, evento)

    def limpar_eventos(self):
        if hasattr(self.interface, 'evento_base'):
            self.interface.evento_base.limpar_registros()
            logger.debug("Registros do banco de dados limpos")
