import os
import sys
import logging
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QGroupBox, QCheckBox,
                               QLineEdit, QDateTimeEdit, QFormLayout, QPushButton,
                               QWidget)
from PySide6.QtCore import Signal, QDateTime
from PySide6.QtGui import QIcon, QAction
from GerenciamentoUI.ui_02_GerenciadorBotoesUI import GerenciadorBotoesUI
from GerenciamentoUI.ui_12_Localizador import Localizador
from .fil_02_AdministradorCalendario import AdministradorCalendario
from .fil_03_AdministradorFiltros import AdministradorFiltros

logger = logging.getLogger('FileManager')


class Filtros(QWidget):
    filtroAplicado = Signal()

    def __init__(self, tabela_dados, loc=None):
        super().__init__()
        self.tabela_dados = tabela_dados
        self.gerenciador_botoes = GerenciadorBotoesUI(self)
        self.loc = loc if loc is not None else Localizador()
        self.administrador_calendario = AdministradorCalendario(self)
        self.administrador_filtros = AdministradorFiltros(self)

        self.loc.idioma_alterado.connect(lambda _: self.filtroAplicado.emit())
        self.loc.idioma_alterado.connect(self.atualizar_interface)
        self.loc.idioma_alterado.connect(self.atualizar_status)

        self.setup_ui()

    def atualizar_status(self, *args):
        if hasattr(self.parent(), "atualizar_status"):
            self.parent().atualizar_status()

        else:
            if hasattr(self, "label_contagem"):
                self.label_contagem.setText(self.atualizar_contagem())

    def setup_ui(self):
        base_path = getattr(sys, "_MEIPASS", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        icon_path = os.path.join(base_path, "icones")
        logger.debug(f"Caminho dos ícones: {icon_path}")
        logger.debug(f"Arquivo calendar.ico existe? {os.path.exists(os.path.join(icon_path, 'calendar.ico'))}")
        logger.debug(f"Arquivo clear_button3.ico existe? {os.path.exists(os.path.join(icon_path, 'clear_button3.ico'))}")

        layout = QVBoxLayout(self)

        grupo_operacao = QGroupBox(self.loc.get_text("operation_filter"))
        layout_operacao = QVBoxLayout()
        self.checkboxes_operacao = {}
        for op in ["op_moved", "op_renamed", "op_added", "op_deleted", "op_modified"]:
            cb = QCheckBox(self.loc.get_text(op))
            cb.setChecked(True)
            cb.stateChanged.connect(self.on_filtro_alterado)
            self.checkboxes_operacao[op] = cb
            layout_operacao.addWidget(cb)

        grupo_operacao.setLayout(layout_operacao)

        grupo_busca = QGroupBox(self.loc.get_text("search"))
        layout_busca = QHBoxLayout()
        self.campo_busca = QLineEdit()
        self.campo_busca.textChanged.connect(self.administrador_filtros.aplicar_filtros)
        layout_busca.addWidget(self.campo_busca)
        grupo_busca.setLayout(layout_busca)

        grupo_extensao = QGroupBox(self.loc.get_text("extension_filter"))
        layout_extensao = QHBoxLayout()
        self.campo_extensao = QLineEdit()
        self.campo_extensao.setPlaceholderText("pdf, txt, doc...")
        self.campo_extensao.textChanged.connect(self.administrador_filtros.aplicar_filtros)
        layout_extensao.addWidget(self.campo_extensao)
        grupo_extensao.setLayout(layout_extensao)

        grupo_data = QGroupBox(self.loc.get_text("date_filter"))
        layout_data = QFormLayout()

        self.ignorar_mover = QCheckBox(self.loc.get_text("ignore_move_filter"))
        self.ignorar_mover.setChecked(True)
        self.ignorar_mover.stateChanged.connect(self.administrador_filtros.aplicar_filtros)
        layout_data.addRow(self.ignorar_mover)

        self.ignorar_renomeados = QCheckBox(self.loc.get_text("ignore_rename_filter"))
        self.ignorar_renomeados.setChecked(True)
        self.ignorar_renomeados.stateChanged.connect(self.administrador_filtros.aplicar_filtros)
        layout_data.addRow(self.ignorar_renomeados)

        self.ignorar_adicionados = QCheckBox(self.loc.get_text("ignore_add_filter"))
        self.ignorar_adicionados.setChecked(True)
        self.ignorar_adicionados.stateChanged.connect(self.administrador_filtros.aplicar_filtros)
        layout_data.addRow(self.ignorar_adicionados)

        self.ignorar_excluidos = QCheckBox(self.loc.get_text("ignore_delete_filter"))
        self.ignorar_excluidos.setChecked(True)
        self.ignorar_excluidos.stateChanged.connect(self.administrador_filtros.aplicar_filtros)
        layout_data.addRow(self.ignorar_excluidos)

        self.ignorar_data_modificados = QCheckBox(self.loc.get_text("ignore_modified_filter"))
        self.ignorar_data_modificados.setChecked(True)
        self.ignorar_data_modificados.stateChanged.connect(self.administrador_filtros.aplicar_filtros)
        layout_data.addRow(self.ignorar_data_modificados)

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

        layout.addWidget(grupo_operacao)
        layout.addWidget(grupo_busca)
        layout.addWidget(grupo_extensao)
        layout.addWidget(grupo_data)

        self.gerenciador_botoes.add_button_with_label(layout, self.loc.get_text("clear_filters"), 'clear_button3.ico', self.administrador_filtros.limpar_filtros, icon_path)

        layout.addStretch()

        self.sincronizar_com_menu_principal()

    def on_filtro_alterado(self):
        self.administrador_filtros.aplicar_filtros()
        self.administrador_filtros.sincronizar_menu_principal_com_filtros()

    def sincronizar_com_menu_principal(self):
        from PySide6.QtWidgets import QApplication
        main_window = None

        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'gerenciador_menus_ui'):
                main_window = widget
                break

        if main_window:
            menu_bar = main_window.menuBar()
            menu_configuracoes = None
            submenu_filtros = None

            for action in menu_bar.actions():
                if action.text() == self.loc.get_text("settings"):
                    menu_configuracoes = action.menu()
                    break

            if menu_configuracoes:
                for action in menu_configuracoes.actions():
                    if action.text() == self.loc.get_text("filters"):
                        submenu_filtros = action.menu()
                        break

            if submenu_filtros:
                for acao in submenu_filtros.actions():
                    if hasattr(acao, 'data') and callable(acao.data):
                        filtro = acao.data()
                        if isinstance(filtro, str) and filtro in self.checkboxes_operacao:
                            self.checkboxes_operacao[filtro].blockSignals(True)
                            self.checkboxes_operacao[filtro].setChecked(acao.isChecked())
                            self.checkboxes_operacao[filtro].blockSignals(False)

            else:
                for acao in main_window.findChildren(QAction):
                    if hasattr(acao, 'data') and callable(acao.data):
                        filtro = acao.data()
                        if isinstance(filtro, str) and filtro in self.checkboxes_operacao:
                            self.checkboxes_operacao[filtro].blockSignals(True)
                            self.checkboxes_operacao[filtro].setChecked(acao.isChecked())
                            self.checkboxes_operacao[filtro].blockSignals(False)

    def verificar_filtro_operacao(self, tipo_operacao_traduzido):
        return self.administrador_filtros.verificar_filtro_operacao(tipo_operacao_traduzido)

    def atualizar_contagem(self):
        return self.administrador_filtros.atualizar_contagem()

    def atualizar_interface(self, idioma=None):
        grupo_operacao = self.findChild(QGroupBox, "grupo_operacao")
        if grupo_operacao:
            grupo_operacao.setTitle(self.loc.get_text("operation_filter"))
            for cb in self.checkboxes_operacao.values():
                texto_original = cb.text()
                cb.setText(self.loc.get_text(texto_original))

        grupo_busca = self.findChild(QGroupBox, "grupo_busca")
        if grupo_busca:
            grupo_busca.setTitle(self.loc.get_text("search"))

        grupo_extensao = self.findChild(QGroupBox, "grupo_extensao")
        if grupo_extensao:
            grupo_extensao.setTitle(self.loc.get_text("extension_filter"))

        grupo_data = self.findChild(QGroupBox)
        if grupo_data and grupo_data.title() == self.loc.get_text("date_filter"):
            grupo_data.setTitle(self.loc.get_text("date_filter"))

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

    def limpar_filtros(self):
        self.administrador_filtros.limpar_filtros()
        self.filtroAplicado.emit()
