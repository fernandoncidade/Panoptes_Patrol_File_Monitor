class Inicializador:
    @staticmethod
    def inicializar_componentes(interface):
        from utils.LogManager import LogManager
        logger = LogManager.get_logger()
        logger.info("Inicializando componentes básicos da UI")

        from PySide6.QtCore import QMutex
        from PySide6.QtWidgets import QTableWidget, QLabel

        interface.mutex = QMutex()
        interface.tabela_dados = QTableWidget()
        interface.status_bar = interface.statusBar()
        interface.label_contagem = QLabel()
        interface.status_bar.addWidget(interface.label_contagem)

        logger.debug("Componentes básicos da UI inicializados com sucesso")

    @staticmethod
    def inicializar_gerenciadores(interface):
        from utils.LogManager import LogManager
        logger = LogManager.get_logger()
        logger.debug("Inicializando gerenciadores")

        from Observador.ob_02_BaseEvento import BaseEvento
        from Observador.ob_10_GerenciadorColunas import GerenciadorColunas
        from Observador.ob_11_GerenciadorTabela import GerenciadorTabela
        from GerenciamentoUI.ui_01_GerenciadorBotoes import GerenciadorBotoes
        from GerenciamentoUI.ui_02_GerenciadorBotoesUI import GerenciadorBotoesUI
        from GerenciamentoUI.ui_03_GerenciadorMenusUI import GerenciadorMenusUI
        from GerenciamentoUI.ui_04_GerenciadorEventosUI import GerenciadorEventosUI
        from GerenciamentoUI.ui_05_GerenciadorProgressoUI import GerenciadorProgressoUI
        from GerenciamentoUI.ui_06_GerenciadorEstatisticasUI import GerenciadorEstatisticasUI
        from Filtros.fil_01_Filtros import Filtros

        interface.evento_base = BaseEvento(interface)
        interface.evento_base.set_callback(interface.adicionar_evento)
        interface.gerenciador_colunas = GerenciadorColunas(interface)
        interface.gerenciador_tabela = GerenciadorTabela(interface)
        interface.gerenciador_botoes = GerenciadorBotoes(interface, interface.loc)
        interface.gerenciador_botoes_ui = GerenciadorBotoesUI(interface)
        interface.painel_filtros = Filtros(interface.tabela_dados, interface.loc)
        interface.painel_filtros.filtroAplicado.connect(interface.atualizar_status)
        interface.gerenciador_menus_ui = GerenciadorMenusUI(interface)
        interface.gerenciador_eventos_ui = GerenciadorEventosUI(interface)
        interface.gerenciador_progresso_ui = GerenciadorProgressoUI(interface)
        interface.gerenciador_estatisticas_ui = GerenciadorEstatisticasUI(interface)

        interface.tipos_operacao = {
            "op_renamed": interface.loc.get_text("op_renamed"),
            "op_added": interface.loc.get_text("op_added"),
            "op_deleted": interface.loc.get_text("op_deleted"),
            "op_modified": interface.loc.get_text("op_modified"),
            "op_moved": interface.loc.get_text("op_moved"),
            "op_scanned": interface.loc.get_text("op_scanned")
        }

        logger.debug("Gerenciadores inicializados com sucesso")

    @staticmethod
    def inicializar_atributos(interface):
        interface.diretorio_atual = None
        interface.ultimo_salvamento = None
        interface.excluidos_recentemente = {}
        interface.observador = None
        interface.contador_eventos = 0
        interface.ultimo_update_status = 0
