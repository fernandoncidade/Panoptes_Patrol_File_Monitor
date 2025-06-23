from PySide6.QtCore import Slot
from PySide6.QtWidgets import QMainWindow, QApplication

from utils.LogManager import LogManager
logger = LogManager.get_logger()
log_file = LogManager.get_log_file()

from .ic_02_Inicializador import Inicializador

import matplotlib
matplotlib.use('QtAgg')

from GerenciamentoUI.ui_08_GerenciadorEventosArquivo import GerenciadorEventosArquivo
from GerenciamentoUI.ui_07_GerenciadorDados import GerenciadorDados
from GerenciamentoUI.ui_09_GerenciadorMonitoramento import GerenciadorMonitoramento
from GerenciamentoUI.ui_10_GerenciadorLimpeza import GerenciadorLimpeza
from GerenciamentoUI.ui_12_Localizador import Localizador

from .ic_03_Configurador import Configurador
from .ic_04_Atualizador import Atualizador
from .ic_05_GerenciadorProgresso import GerenciadorProgresso
from .ic_07_ManipuladorTabela import ManipuladorTabela
from .ic_08_Internacionalizador import Internacionalizador


class InterfaceMonitor(QMainWindow):
    def __init__(self):
        try:
            logger.info("Iniciando a aplicação Panoptes_Patrol")
            super().__init__()

            logger.debug("Inicializando o localizador")
            self.loc = Localizador()
            self.loc.verificar_traducoes_ausentes()
            self.loc.idioma_alterado.connect(self.atualizar_status)
            self.loc.idioma_alterado.connect(self.atualizar_tradutor_qt)

            Inicializador.inicializar_atributos(self)
            Inicializador.inicializar_componentes(self)
            Inicializador.inicializar_gerenciadores(self)

            logger.debug("Configurando interface principal")
            self.configurar_tabela()
            self.setup_ui()
            self.setup_menu_bar()

            self.gerenciador_eventos_arquivo = GerenciadorEventosArquivo(self)
            self.gerenciador_dados = GerenciadorDados(self)
            self.gerenciador_monitoramento = GerenciadorMonitoramento(self)
            self.gerenciador_limpeza = GerenciadorLimpeza(self)

            logger.info("Inicialização da aplicação concluída com sucesso")

        except Exception as e:
            logger.critical(f"Erro fatal na inicialização: {e}", exc_info=True)
            QApplication.quit()

    def setup_ui(self):
        Configurador.setup_ui(self)

    def setup_menu_bar(self):
        Configurador.setup_menu_bar(self)

    def atualizar_interface(self):
        Atualizador.atualizar_interface(self)

    def abrir_janela_filtros(self):
        Atualizador.abrir_janela_filtros(self)

    def atualizar_status(self, *args):
        Atualizador.atualizar_status(self, *args)

    def configurar_tabela(self):
        ManipuladorTabela.configurar_tabela(self)

    def verificar_movimentacao(self, evento):
        return self.gerenciador_eventos_arquivo.verificar_movimentacao(evento)

    def adicionar_evento(self, evento):
        self.gerenciador_eventos_arquivo.adicionar_evento(evento)

    def selecionar_diretorio(self):
        logger.info("Usuário iniciou seleção de diretório")
        self.gerenciador_botoes.selecionar_diretorio()

    def alternar_analise_diretorio(self):
        logger.info("Usuário alternando análise de diretório")
        self.gerenciador_botoes.alternar_analise_diretorio()

    def salvar_dados(self):
        self.gerenciador_dados.salvar_dados()

    def abrir_salvar_como(self):
        self.gerenciador_dados.abrir_salvar_como()

    def mostrar_estatisticas(self):
        self.gerenciador_estatisticas_ui.mostrar_estatisticas()

    def salvar_todos_graficos(self, gerador):
        self.gerenciador_estatisticas_ui.salvar_todos_graficos(gerador)

    def limpar_dados(self):
        self.gerenciador_limpeza.limpar_dados()

    def sair_aplicacao(self):
        self.close()

    @Slot()
    def criar_barra_progresso(self):
        GerenciadorProgresso.criar_barra_progresso(self)

    @Slot(int, int, int)
    def atualizar_progresso_scan(self, progresso, contador, total):
        GerenciadorProgresso.atualizar_progresso_scan(self, progresso, contador, total)

    def alternar_filtro(self):
        self.gerenciador_eventos_ui.alternar_filtro()

    def alternar_visibilidade_coluna(self):
        self.gerenciador_eventos_ui.alternar_visibilidade_coluna()

    def resetar_colunas(self):
        self.gerenciador_eventos_ui.resetar_colunas()

    def alterar_idioma(self):
        self.gerenciador_eventos_ui.alterar_idioma()

    def atualizar_visibilidade_colunas(self):
        ManipuladorTabela.atualizar_visibilidade_colunas(self)

    def reiniciar_sistema_monitoramento(self):
        self.gerenciador_monitoramento.reiniciar_sistema_monitoramento()

    def atualizar_tradutor_qt(self, idioma):
        Internacionalizador.atualizar_tradutor_qt(self, idioma)
