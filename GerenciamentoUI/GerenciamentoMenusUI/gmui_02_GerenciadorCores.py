import os
import sys
import json
from PySide6.QtGui import QColor
from PySide6.QtCore import QThread, Signal
from utils.LogManager import LogManager

logger = LogManager.get_logger()


class GerenciadorCores:
    def __init__(self, interface_principal):
        self.interface = interface_principal
        self.loc = interface_principal.loc

        self.cores_operacoes = {
            "op_renamed": "#00ff00",
            "op_added": "#0000ff",
            "op_deleted": "#ff0000",
            "op_modified": "#ff6200",
            "op_moved": "#ff00ff",
            "op_scanned": "#808080"
        }
        self.carregar_cores()

    def carregar_cores(self):
        try:
            config_dir = self._obter_diretorio_config()
            cores_path = os.path.join(config_dir, "cores_config.json")
            if os.path.exists(cores_path):
                with open(cores_path, 'r', encoding='utf-8') as f:
                    cores_salvas = json.load(f)

                for tipo, cor in cores_salvas.get('cores_operacoes', {}).items():
                    if tipo in self.cores_operacoes:
                        self.cores_operacoes[tipo] = cor

                logger.info("Configurações de cores carregadas com sucesso")

            else:
                logger.info("Arquivo de configuração de cores não encontrado, usando valores padrão")

        except Exception as e:
            logger.error(f"Erro ao carregar configurações de cores: {e}", exc_info=True)

    def salvar_cores(self):
        try:
            config_dir = self._obter_diretorio_config()
            cores_path = os.path.join(config_dir, "cores_config.json")

            os.makedirs(config_dir, exist_ok=True)

            cores_config = {'cores_operacoes': self.cores_operacoes}
            with open(cores_path, 'w', encoding='utf-8') as f:
                json.dump(cores_config, f, indent=4)

            logger.info("Configurações de cores salvas com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar configurações de cores: {e}", exc_info=True)
            return False

    def _obter_diretorio_config(self):
        from pathlib import Path
        try:
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)

            else:
                base_path = Path(__file__).resolve().parents[2]

            config_dir = os.path.join(base_path, "config")
            return config_dir

        except Exception:
            return Path(__file__).resolve().parents[2]

    def obter_cor_qcolor(self, tipo_operacao):
        cor_hex = self.cores_operacoes.get(tipo_operacao, "#333333")
        return QColor(cor_hex)

    def obter_cor_hex(self, tipo_operacao):
        return self.cores_operacoes.get(tipo_operacao, "#333333")

    def definir_cor(self, tipo_operacao, cor_hex):
        if tipo_operacao in self.cores_operacoes:
            self.cores_operacoes[tipo_operacao] = cor_hex
            return True

        return False

    def atualizar_cores_no_sistema(self):
        from GerenciamentoUI.GerenciamentoMenusUI.gmui_02_GerenciadorCores import ThreadAtualizarCores
        self.thread_cores = ThreadAtualizarCores(self, self.interface)
        self.thread_cores.sinal_concluido.connect(self.interface.update)
        self.thread_cores.start()

    def _atualizar_cores_no_sistema_threadsafe(self):
        if hasattr(self.interface, 'gerenciador_tabela'):
            self.interface.gerenciador_tabela.atualizacao_pendente = True
            self.interface.gerenciador_tabela.atualizar_dados_tabela(self.interface.tabela_dados)

        if hasattr(self.interface, 'gerenciador_estatisticas_ui') and hasattr(self.interface.gerenciador_estatisticas_ui, 'gerador_atual'):
            if self.interface.gerenciador_estatisticas_ui.gerador_atual:
                self.interface.gerenciador_estatisticas_ui.gerador_atual.atualizar_textos_traduzidos()


class ThreadAtualizarCores(QThread):
    sinal_concluido = Signal()

    def __init__(self, gerenciador_cores, interface):
        super().__init__()
        self.gerenciador_cores = gerenciador_cores
        self.interface = interface

    def run(self):
        try:
            self.gerenciador_cores._atualizar_cores_no_sistema_threadsafe()

        finally:
            self.sinal_concluido.emit()
