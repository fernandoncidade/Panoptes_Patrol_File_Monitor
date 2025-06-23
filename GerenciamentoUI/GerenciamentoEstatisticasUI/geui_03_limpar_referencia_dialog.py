from utils.LogManager import LogManager

logger = LogManager.get_logger()

def limpar_referencia_dialog(self):
    self.dialog_estatisticas = None
    self.checkboxes_graficos.clear()
    self.graficos_dados.clear()
    self.painel_selecao = None
    self.splitter = None
