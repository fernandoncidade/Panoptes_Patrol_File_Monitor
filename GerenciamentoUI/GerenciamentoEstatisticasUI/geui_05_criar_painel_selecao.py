import os
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QScrollArea, QCheckBox, QFrame, QPushButton)
from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _criar_painel_selecao(self, graficos=None):
    container = QWidget()
    container_layout = QHBoxLayout()
    container_layout.setContentsMargins(0, 0, 0, 0)
    container_layout.setSpacing(0)

    texto_ocultar = (self.loc.get_text("hide_selection_panel") if "hide_selection_panel" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Ocultar Painel de Seleção")
    self.btn_toggle_painel = self._criar_botao_toggle_painel(texto_ocultar)

    largura_botao = 25
    self.btn_toggle_painel.setFixedWidth(largura_botao)

    container_layout.addWidget(self.btn_toggle_painel, 0, Qt.AlignLeft | Qt.AlignTop)

    panel = QFrame()
    panel.setFrameStyle(QFrame.StyledPanel)
    max_width = self._calcular_largura_ideal(graficos)
    self.tamanho_painel_original = max_width
    panel.setFixedWidth(max_width)

    layout = QVBoxLayout()
    layout.setContentsMargins(5, 5, 5, 5)

    self.titulo_selecionar_graficos = QLabel(self.loc.get_text("select_graphs") if "select_graphs" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Selecionar Gráficos")
    layout.addWidget(self.titulo_selecionar_graficos)

    scroll_area = QScrollArea()
    scroll_widget = QWidget()

    self.checkboxes_layout = QVBoxLayout()
    self.checkbox_todos = QCheckBox(self.loc.get_text("select_all") if "select_all" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Selecionar Todos")
    self.checkbox_todos.setChecked(True)
    self.checkbox_todos.setTristate(True)
    self.checkbox_todos.clicked.connect(self._alternar_todos_checkboxes)
    self.checkboxes_layout.addWidget(self.checkbox_todos)

    separador = QFrame()
    separador.setFrameStyle(QFrame.HLine)
    self.checkboxes_layout.addWidget(separador)
    self.checkboxes_layout.addStretch()

    scroll_widget.setLayout(self.checkboxes_layout)
    scroll_area.setWidget(scroll_widget)
    scroll_area.setWidgetResizable(True)
    scroll_area.setMinimumHeight(500)
    layout.addWidget(scroll_area, 1)

    buttons_layout = QVBoxLayout()
    buttons_layout.setSpacing(5)

    base_path = getattr(sys, "_MEIPASS", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    icon_path = os.path.join(base_path, "icones")

    self.btn_salvar_selecionados = QPushButton(self.loc.get_text("save_selected") if "save_selected" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Salvar Selecionados")
    self.btn_salvar_selecionados.setIcon(QIcon(os.path.join(icon_path, "salvar.ico")))
    self.btn_salvar_selecionados.clicked.connect(self._salvar_graficos_selecionados)
    buttons_layout.addWidget(self.btn_salvar_selecionados)

    self.btn_salvar_todos = QPushButton(self.loc.get_text("save_all"))
    self.btn_salvar_todos.setIcon(QIcon(os.path.join(icon_path, "salvar.ico")))
    self.btn_salvar_todos.clicked.connect(lambda: self.salvar_todos_graficos(self.gerador_atual))
    buttons_layout.addWidget(self.btn_salvar_todos)

    self.btn_atualizar = QPushButton(self.loc.get_text("refresh"))
    self.btn_atualizar.setIcon(QIcon(os.path.join(icon_path, "atualizar.ico")))
    self.btn_atualizar.clicked.connect(lambda: self._atualizar_graficos(self.dialog_estatisticas))
    buttons_layout.addWidget(self.btn_atualizar)

    layout.addLayout(buttons_layout, 0)
    panel.setLayout(layout)

    container_layout.addWidget(panel, 1, Qt.AlignTop)

    largura_total = largura_botao + max_width
    container.setFixedWidth(largura_total)
    container.setLayout(container_layout)
    self.painel_selecao_interno = panel
    return container
