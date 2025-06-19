import os
import sys
from utils.LogManager import LogManager
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar


class Configurador:
    @staticmethod
    def setup_ui(interface):
        logger = LogManager.get_logger()
        logger.debug("Configurando interface principal")

        widget_central = QWidget()

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            icon_path = os.path.join(base_path, "icones")

        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            icon_path = os.path.join(base_path, "icones")

        logger.debug(f"Caminho dos ícones: {icon_path}")

        interface.setWindowTitle(interface.loc.get_text("window_title"))
        interface.setWindowIcon(QIcon(os.path.join(icon_path, "manager_files.ico")))
        interface.setCentralWidget(widget_central)
        interface.setGeometry(100, 100, 900, 500)

        layout_principal = QHBoxLayout(widget_central)
        layout_lateral = QVBoxLayout()
        layout_lateral_inferior = QVBoxLayout()
        layout_lateral_inferior.addStretch(1)
        layout_lateral_inferior.setContentsMargins(10, 10, 10, 10)

        interface.gerenciador_botoes_ui.add_button_with_label(layout_lateral_inferior, interface.loc.get_text("select_dir"), 'selecione.ico', interface.selecionar_diretorio, icon_path, "select_dir")
        interface.gerenciador_botoes_ui.add_button_with_label(layout_lateral_inferior, interface.loc.get_text("start_stop"), 'analyze.ico', interface.alternar_analise_diretorio, icon_path, "start_stop")
        interface.gerenciador_botoes_ui.add_button_with_label(layout_lateral_inferior, interface.loc.get_text("save_as"), 'save_as.ico', interface.abrir_salvar_como, icon_path, "save_as")
        interface.gerenciador_botoes_ui.add_button_with_label(layout_lateral_inferior, interface.loc.get_text("statistics"), 'statistics.ico', interface.mostrar_estatisticas, icon_path, "statistics")
        interface.gerenciador_botoes_ui.add_button_with_label(layout_lateral_inferior, interface.loc.get_text("clear_data"), 'clear.ico', interface.limpar_dados, icon_path, "clear_data")

        layout_lateral.addLayout(layout_lateral_inferior)
        layout_conteudo = QVBoxLayout()

        interface.rotulo_diretorio = QLabel(interface.loc.get_text("no_dir"))
        interface.rotulo_resultado = QLabel(interface.loc.get_text("select_to_start"))

        interface.rotulo_contador_eventos = QLabel(f"{interface.loc.get_text('events_monitored')}: 0")
        interface.rotulo_contador_eventos.setObjectName("rotulo_contador_eventos")

        from Observador.ob_08_EventoMovido import _atualizar_contador_eventos
        interface.loc.idioma_alterado.connect(lambda _: _atualizar_contador_eventos(interface))

        layout_info = QHBoxLayout()
        layout_info.addWidget(interface.rotulo_resultado, 1)
        layout_info.addWidget(interface.rotulo_contador_eventos, 0)

        interface.barra_progresso = QProgressBar(interface)
        interface.barra_progresso.setMaximum(100)
        interface.barra_progresso.setMinimum(0)
        interface.barra_progresso.setValue(0)
        interface.barra_progresso.setTextVisible(True)
        interface.barra_progresso.setFormat("%p%")
        interface.barra_progresso.setFixedHeight(20)
        interface.barra_progresso.hide()

        layout_conteudo.addWidget(interface.rotulo_diretorio)
        layout_conteudo.addLayout(layout_info)
        layout_conteudo.addWidget(interface.barra_progresso)
        layout_conteudo.addWidget(interface.tabela_dados)

        layout_principal.addLayout(layout_lateral)
        layout_principal.addLayout(layout_conteudo, stretch=1)

        interface.atualizar_status()
        logger.debug("Interface principal configurada com sucesso")

    @staticmethod
    def setup_menu_bar(interface):
        logger = LogManager.get_logger()
        logger.debug("Configurando barra de menu")
        interface.gerenciador_menus_ui.criar_menu_principal()
        logger.debug("Barra de menu configurada com sucesso")
