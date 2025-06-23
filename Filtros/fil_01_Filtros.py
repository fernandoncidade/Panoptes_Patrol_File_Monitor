import os
import sys
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox,
                               QLineEdit, QDateTimeEdit, QFormLayout, QPushButton,
                               QWidget)
from PySide6.QtCore import Signal, QDateTime
from PySide6.QtGui import QIcon, QAction
from GerenciamentoUI.ui_02_GerenciadorBotoesUI import GerenciadorBotoesUI
from GerenciamentoUI.ui_12_Localizador import Localizador
from .fil_02_AdministradorCalendario import AdministradorCalendario
from .fil_03_AdministradorFiltros import AdministradorFiltros
from utils.LogManager import LogManager


class Filtros(QWidget):
    filtroAplicado = Signal()

    def __init__(self, tabela_dados, loc=None):
        super().__init__()
        logger = LogManager.get_logger()
        logger.debug("Inicializando módulo de Filtros")

        self.tabela_dados = tabela_dados
        self.gerenciador_botoes = GerenciadorBotoesUI(self)

        try:
            self.loc = loc if loc is not None else Localizador()
            logger.debug(f"Localizador configurado com idioma: {self.loc.idioma_atual}")

        except Exception as e:
            logger.error(f"Erro ao configurar localizador: {e}", exc_info=True)
            from GerenciamentoUI.ui_12_Localizador import Localizador
            self.loc = Localizador()

        self.administrador_calendario = AdministradorCalendario(self)
        self.administrador_filtros = AdministradorFiltros(self)

        self.loc.idioma_alterado.connect(lambda _: self.filtroAplicado.emit())
        self.loc.idioma_alterado.connect(self.atualizar_interface)
        self.loc.idioma_alterado.connect(self.atualizar_status)

        logger.debug("Configurando interface de filtros")
        self.setup_ui()
        logger.info("Módulo de Filtros inicializado com sucesso")

    def atualizar_status(self, *args):
        try:
            if hasattr(self.parent(), "atualizar_status"):
                self.parent().atualizar_status()

            else:
                if hasattr(self, "label_contagem"):
                    self.label_contagem.setText(self.atualizar_contagem())

            LogManager.get_logger().debug("Status atualizado nos filtros")

        except Exception as e:
            LogManager.get_logger().error(f"Erro ao atualizar status dos filtros: {e}", exc_info=True)

    def setup_ui(self):
        logger = LogManager.get_logger()
        try:
            if getattr(sys, 'frozen', False):
                base_path = sys._MEIPASS

            else:
                base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

            icon_path = os.path.join(base_path, "icones")
            logger.debug(f"Caminho dos ícones: {icon_path}")
            logger.debug(f"Arquivo calendar.ico existe? {os.path.exists(os.path.join(icon_path, 'calendar.ico'))}")
            logger.debug(f"Arquivo clear_button3.ico existe? {os.path.exists(os.path.join(icon_path, 'clear_button3.ico'))}")

            layout = QVBoxLayout(self)

            grupo_operacao = QGroupBox(self.loc.get_text("operation_filter"))
            grupo_operacao.setObjectName("grupo_operacao")
            layout_operacao = QVBoxLayout()
            self.checkboxes_operacao = {}
            for op in ["op_moved", "op_renamed", "op_added", "op_deleted", "op_modified", "op_scanned"]:
                cb = QCheckBox(self.loc.get_text(op))
                cb.setChecked(True)
                cb.stateChanged.connect(self.on_filtro_alterado)
                self.checkboxes_operacao[op] = cb
                layout_operacao.addWidget(cb)
                logger.debug(f"Checkbox adicionado para operação: {op}")

            grupo_operacao.setLayout(layout_operacao)

            # Grupo de busca
            grupo_busca = QGroupBox(self.loc.get_text("search"))
            grupo_busca.setObjectName("grupo_busca")
            layout_busca = QHBoxLayout()
            self.campo_busca = QLineEdit()
            self.campo_busca.textChanged.connect(self.administrador_filtros.aplicar_filtros)
            layout_busca.addWidget(self.campo_busca)
            grupo_busca.setLayout(layout_busca)

            # Grupo de filtro por extensão
            grupo_extensao = QGroupBox(self.loc.get_text("extension_filter"))
            grupo_extensao.setObjectName("grupo_extensao")
            layout_extensao = QHBoxLayout()
            self.campo_extensao = QLineEdit()
            self.campo_extensao.setPlaceholderText("pdf, txt, doc...")
            self.campo_extensao.textChanged.connect(self.administrador_filtros.aplicar_filtros)
            layout_extensao.addWidget(self.campo_extensao)
            grupo_extensao.setLayout(layout_extensao)

            # Grupo de filtro por data
            grupo_data = QGroupBox(self.loc.get_text("date_filter"))
            layout_data = QFormLayout()

            # Checkboxes para ignorar tipos de operações na filtragem por data
            self.ignorar_mover = QCheckBox(self.loc.get_text("ignore_move_filter"))
            self.ignorar_mover.setChecked(AdministradorFiltros.filtros_estado.get("ignorar_mover", True))
            self.ignorar_mover.stateChanged.connect(self.administrador_filtros.aplicar_filtros)
            layout_data.addRow(self.ignorar_mover)

            self.ignorar_renomeados = QCheckBox(self.loc.get_text("ignore_rename_filter"))
            self.ignorar_renomeados.setChecked(AdministradorFiltros.filtros_estado.get("ignorar_renomeados", True))
            self.ignorar_renomeados.stateChanged.connect(self.administrador_filtros.aplicar_filtros)
            layout_data.addRow(self.ignorar_renomeados)

            self.ignorar_adicionados = QCheckBox(self.loc.get_text("ignore_add_filter"))
            self.ignorar_adicionados.setChecked(AdministradorFiltros.filtros_estado.get("ignorar_adicionados", True))
            self.ignorar_adicionados.stateChanged.connect(self.administrador_filtros.aplicar_filtros)
            layout_data.addRow(self.ignorar_adicionados)

            self.ignorar_excluidos = QCheckBox(self.loc.get_text("ignore_delete_filter"))
            self.ignorar_excluidos.setChecked(AdministradorFiltros.filtros_estado.get("ignorar_excluidos", True))
            self.ignorar_excluidos.stateChanged.connect(self.administrador_filtros.aplicar_filtros)
            layout_data.addRow(self.ignorar_excluidos)

            self.ignorar_data_modificados = QCheckBox(self.loc.get_text("ignore_modified_filter"))
            self.ignorar_data_modificados.setChecked(AdministradorFiltros.filtros_estado.get("ignorar_data_modificados", True))
            self.ignorar_data_modificados.stateChanged.connect(self.administrador_filtros.aplicar_filtros)
            layout_data.addRow(self.ignorar_data_modificados)

            self.ignorar_escaneados = QCheckBox(self.loc.get_text("ignore_scanned_filter"))
            self.ignorar_escaneados.setChecked(AdministradorFiltros.filtros_estado.get("ignorar_escaneados", True))
            self.ignorar_escaneados.stateChanged.connect(self.administrador_filtros.aplicar_filtros)
            layout_data.addRow(self.ignorar_escaneados)

            # Seletores de data e hora
            container_data_inicial = QHBoxLayout()
            self.data_inicial = QDateTimeEdit()
            self.data_inicial.setDateTime(QDateTime.currentDateTime().addDays(-30))
            self.data_inicial.dateTimeChanged.connect(self.administrador_filtros.aplicar_filtros)
            container_data_inicial.addWidget(self.data_inicial)

            btn_calendario_inicial = QPushButton()
            btn_calendario_inicial.setIcon(QIcon(os.path.join(icon_path, "calendar.ico")))
            btn_calendario_inicial.setFixedSize(24, 24)
            btn_calendario_inicial.clicked.connect(lambda: self.administrador_calendario.mostrar_calendario(self.data_inicial))
            container_data_inicial.addWidget(btn_calendario_inicial)

            container_data_final = QHBoxLayout()
            self.data_final = QDateTimeEdit()
            self.data_final.setDateTime(QDateTime.currentDateTime())
            self.data_final.dateTimeChanged.connect(self.administrador_filtros.aplicar_filtros)
            container_data_final.addWidget(self.data_final)

            btn_calendario_final = QPushButton()
            btn_calendario_final.setIcon(QIcon(os.path.join(icon_path, "calendar.ico")))
            btn_calendario_final.setFixedSize(24, 24)
            btn_calendario_final.clicked.connect(lambda: self.administrador_calendario.mostrar_calendario(self.data_final))
            container_data_final.addWidget(btn_calendario_final)

            layout_data.addRow(self.loc.get_text("start_date"), container_data_inicial)
            layout_data.addRow(self.loc.get_text("end_date"), container_data_final)
            grupo_data.setLayout(layout_data)

            # Adiciona todos os grupos ao layout principal
            layout.addWidget(grupo_operacao)
            layout.addWidget(grupo_busca)
            layout.addWidget(grupo_extensao)
            layout.addWidget(grupo_data)

            # Adiciona botão para limpar filtros
            self.gerenciador_botoes.add_button_with_label(
                layout, 
                self.loc.get_text("clear_filters"), 
                'clear_button3.ico', 
                self.administrador_filtros.limpar_filtros, 
                icon_path
            )

            layout.addStretch()

            # Sincroniza com o menu principal
            self.sincronizar_com_menu_principal()
            logger.info("Interface de filtros configurada com sucesso")

        except Exception as e:
            logger.error(f"Erro ao configurar interface de filtros: {e}", exc_info=True)

    def on_filtro_alterado(self):
        logger = LogManager.get_logger()
        try:
            logger.debug("Filtro alterado, aplicando mudanças")
            self.administrador_filtros.aplicar_filtros()
            self.administrador_filtros.sincronizar_menu_principal_com_filtros()

        except Exception as e:
            logger.error(f"Erro ao processar alteração de filtro: {e}", exc_info=True)

    def sincronizar_com_menu_principal(self):
        logger = LogManager.get_logger()
        try:
            logger.debug("Sincronizando filtros com o menu principal")
            from PySide6.QtWidgets import QApplication
            main_window = None

            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'gerenciador_menus_ui'):
                    main_window = widget
                    logger.debug("Janela principal encontrada")
                    break

            if main_window:
                menu_bar = main_window.menuBar()
                menu_configuracoes = None
                submenu_filtros = None

                # Busca o menu de configurações
                for action in menu_bar.actions():
                    if action.text() == self.loc.get_text("settings"):
                        menu_configuracoes = action.menu()
                        logger.debug("Menu de configurações encontrado")
                        break

                # Busca o submenu de filtros
                if menu_configuracoes:
                    for action in menu_configuracoes.actions():
                        if action.text() == self.loc.get_text("filters"):
                            submenu_filtros = action.menu()
                            logger.debug("Submenu de filtros encontrado")
                            break

                # Sincroniza os checkboxes com as ações do menu
                if submenu_filtros:
                    logger.debug("Sincronizando checkboxes com ações do submenu de filtros")
                    for acao in submenu_filtros.actions():
                        if hasattr(acao, 'data') and callable(acao.data):
                            filtro = acao.data()
                            if isinstance(filtro, str) and filtro in self.checkboxes_operacao:
                                self.checkboxes_operacao[filtro].blockSignals(True)
                                self.checkboxes_operacao[filtro].setChecked(acao.isChecked())
                                self.checkboxes_operacao[filtro].blockSignals(False)
                                logger.debug(f"Checkbox '{filtro}' sincronizado com estado: {acao.isChecked()}")

                else:
                    logger.debug("Buscando ações no contexto global da janela principal")
                    for acao in main_window.findChildren(QAction):
                        if hasattr(acao, 'data') and callable(acao.data):
                            filtro = acao.data()
                            if isinstance(filtro, str) and filtro in self.checkboxes_operacao:
                                self.checkboxes_operacao[filtro].blockSignals(True)
                                self.checkboxes_operacao[filtro].setChecked(acao.isChecked())
                                self.checkboxes_operacao[filtro].blockSignals(False)
                                logger.debug(f"Checkbox '{filtro}' sincronizado com estado: {acao.isChecked()}")

            else:
                logger.warning("Janela principal não encontrada para sincronização de filtros")

        except Exception as e:
            logger.error(f"Erro ao sincronizar filtros com menu principal: {e}", exc_info=True)

    def verificar_filtro_operacao(self, tipo_operacao_traduzido):
        try:
            resultado = self.administrador_filtros.verificar_filtro_operacao(tipo_operacao_traduzido)
            return resultado

        except Exception as e:
            LogManager.get_logger().error(f"Erro ao verificar filtro de operação: {e}", exc_info=True)
            return True

    def atualizar_contagem(self):
        try:
            resultado = self.administrador_filtros.atualizar_contagem()
            return resultado

        except Exception as e:
            LogManager.get_logger().error(f"Erro ao atualizar contagem: {e}", exc_info=True)
            return self.loc.get_text("items_count").format(0, 0)

    def atualizar_interface(self, idioma=None):
        logger = LogManager.get_logger()
        try:
            logger.debug(f"Atualizando interface de filtros para idioma: {idioma if idioma else self.loc.idioma_atual}")

            # Atualiza título do grupo de operações
            grupo_operacao = self.findChild(QGroupBox, "grupo_operacao")
            if grupo_operacao:
                grupo_operacao.setTitle(self.loc.get_text("operation_filter"))
                for op, cb in self.checkboxes_operacao.items():
                    cb.setText(self.loc.get_text(op))
                    logger.debug(f"Checkbox {op} atualizado para: {self.loc.get_text(op)}")

            # Atualiza título do grupo de busca
            grupo_busca = self.findChild(QGroupBox, "grupo_busca")
            if grupo_busca:
                grupo_busca.setTitle(self.loc.get_text("search"))

            # Atualiza título do grupo de extensões
            grupo_extensao = self.findChild(QGroupBox, "grupo_extensao")
            if grupo_extensao:
                grupo_extensao.setTitle(self.loc.get_text("extension_filter"))

            # Atualiza título do grupo de data
            grupo_data = self.findChild(QGroupBox)
            if grupo_data and grupo_data.title() == self.loc.get_text("date_filter"):
                grupo_data.setTitle(self.loc.get_text("date_filter"))

            # Atualiza textos dos checkboxes de tipos de operação
            if hasattr(self, 'ignorar_mover'):
                self.ignorar_mover.setText(self.loc.get_text("ignore_move_filter"))

            if hasattr(self, 'ignorar_renomeados'):
                self.ignorar_renomeados.setText(self.loc.get_text("ignore_rename_filter"))

            if hasattr(self, 'ignorar_adicionados'):
                self.ignorar_adicionados.setText(self.loc.get_text("ignore_add_filter"))

            if hasattr(self, 'ignorar_excluidos'):
                self.ignorar_excluidos.setText(self.loc.get_text("ignore_delete_filter"))

            if hasattr(self, 'ignorar_data_modificados'):
                self.ignorar_data_modificados.setText(self.loc.get_text("ignore_modified_filter"))

            if hasattr(self, 'ignorar_escaneados'):
                self.ignorar_escaneados.setText(self.loc.get_text("ignore_scanned_filter"))

            logger.debug("Interface de filtros atualizada com sucesso")

        except Exception as e:
            logger.error(f"Erro ao atualizar interface de filtros: {e}", exc_info=True)

    def limpar_filtros(self):
        logger = LogManager.get_logger()
        try:
            logger.info("Limpando todos os filtros")
            self.administrador_filtros.limpar_filtros()
            self.filtroAplicado.emit()
            logger.debug("Filtros limpos e sinal emitido")

        except Exception as e:
            logger.error(f"Erro ao limpar filtros: {e}", exc_info=True)
