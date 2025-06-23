import os
import sys

from utils.LogManager import LogManager
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QDialog, QSplitter, QTabWidget, QApplication

# Importando a classe BotaoRotacionado diretamente
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_30_botao_rotacionado import BotaoRotacionado

# Importando as funções dos outros módulos
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_01_mostrar_estatisticas import mostrar_estatisticas
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_02_salvar_todos_graficos import salvar_todos_graficos
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_03_limpar_referencia_dialog import limpar_referencia_dialog
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_04_atualizar_graficos_apos_mudanca_idioma import atualizar_graficos_apos_mudanca_idioma
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_05_criar_painel_selecao import _criar_painel_selecao
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_06_criar_painel_graficos import _criar_painel_graficos
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_07_criar_botao_toggle_painel import _criar_botao_toggle_painel
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_08_criar_lista_graficos import _criar_lista_graficos
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_09_criar_mapeamento_funcoes import _criar_mapeamento_funcoes
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_10_popular_checkboxes import _popular_checkboxes
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_11_verificar_estado_checkbox_todos import _verificar_estado_checkbox_todos
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_12_alternar_todos_checkboxes import _alternar_todos_checkboxes
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_13_obter_estados_checkboxes import _obter_estados_checkboxes
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_14_gerar_todos_graficos import _gerar_todos_graficos
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_15_atualizar_graficos import _atualizar_graficos
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_16_atualizar_graficos_sem_fechar import _atualizar_graficos_sem_fechar
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_17_regenerar_graficos_existentes import _regenerar_graficos_existentes
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_18_salvar_graficos_selecionados import _salvar_graficos_selecionados
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_19_toggle_painel_selecao import _toggle_painel_selecao
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_20_atualizar_textos_painel_selecao import _atualizar_textos_painel_selecao
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_21_atualizar_textos_checkboxes import _atualizar_textos_checkboxes
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_22_atualizar_layout_apos_mudanca_botao import _atualizar_layout_apos_mudanca_botao
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_23_atualizar_checkboxes_graficos import _atualizar_checkboxes_graficos
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_24_atualizar_abas_graficos import _atualizar_abas_graficos
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_25_atualizar_dados_graficos_com_novos_titulos import _atualizar_dados_graficos_com_novos_titulos
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_26_calcular_largura_ideal import _calcular_largura_ideal
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_27_ajustar_largura_painel_selecao import _ajustar_largura_painel_selecao
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_28_traduzir_botoes_detalhes import _traduzir_botoes_detalhes
from GerenciamentoUI.GerenciamentoEstatisticasUI.geui_29_abrir_diretorio import _abrir_diretorio

logger = LogManager.get_logger()

class GerenciadorEstatisticasUI:
    def __init__(self, interface_principal):
        self.interface = interface_principal
        self.loc = interface_principal.loc
        self.evento_base = interface_principal.evento_base
        self.dialog_estatisticas = None
        self.checkboxes_graficos = {}
        self.tab_widget = None
        self.graficos_dados = {}
        self.painel_selecao = None
        self.splitter = None
        self.painel_recolhido = False
        self.btn_toggle_painel = None
        self.tamanho_painel_original = 0
        self._atualizando_idioma = False
        self.gerador_atual = None

        if hasattr(self.loc, 'idioma_alterado'):
            self.loc.idioma_alterado.connect(self.atualizar_graficos_apos_mudanca_idioma)

    # Atribuição das funções importadas como métodos da classe
    mostrar_estatisticas = mostrar_estatisticas
    salvar_todos_graficos = salvar_todos_graficos
    limpar_referencia_dialog = limpar_referencia_dialog
    atualizar_graficos_apos_mudanca_idioma = atualizar_graficos_apos_mudanca_idioma
    _criar_painel_selecao = _criar_painel_selecao
    _criar_painel_graficos = _criar_painel_graficos
    _criar_botao_toggle_painel = _criar_botao_toggle_painel
    _criar_lista_graficos = _criar_lista_graficos
    _criar_mapeamento_funcoes = _criar_mapeamento_funcoes
    _popular_checkboxes = _popular_checkboxes
    _verificar_estado_checkbox_todos = _verificar_estado_checkbox_todos
    _alternar_todos_checkboxes = _alternar_todos_checkboxes
    _obter_estados_checkboxes = _obter_estados_checkboxes
    _gerar_todos_graficos = _gerar_todos_graficos
    _atualizar_graficos = _atualizar_graficos
    _atualizar_graficos_sem_fechar = _atualizar_graficos_sem_fechar
    _regenerar_graficos_existentes = _regenerar_graficos_existentes
    _salvar_graficos_selecionados = _salvar_graficos_selecionados
    _toggle_painel_selecao = _toggle_painel_selecao
    _atualizar_textos_painel_selecao = _atualizar_textos_painel_selecao
    _atualizar_textos_checkboxes = _atualizar_textos_checkboxes
    _atualizar_layout_apos_mudanca_botao = _atualizar_layout_apos_mudanca_botao
    _atualizar_checkboxes_graficos = _atualizar_checkboxes_graficos
    _atualizar_abas_graficos = _atualizar_abas_graficos
    _atualizar_dados_graficos_com_novos_titulos = _atualizar_dados_graficos_com_novos_titulos
    _calcular_largura_ideal = _calcular_largura_ideal
    _ajustar_largura_painel_selecao = _ajustar_largura_painel_selecao
    _traduzir_botoes_detalhes = _traduzir_botoes_detalhes
    _abrir_diretorio = _abrir_diretorio
