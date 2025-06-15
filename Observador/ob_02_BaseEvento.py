import os
import sys

from Observador.GerenciamentoBaseEvento.gbank_01_set_callback import set_callback
from Observador.GerenciamentoBaseEvento.gbank_02_criar_banco_de_dados import criar_banco_de_dados
from Observador.GerenciamentoBaseEvento.gbank_03_processar_exclusao import processar_exclusao
from Observador.GerenciamentoBaseEvento.gbank_04_registrar_evento_especifico import registrar_evento_especifico
from Observador.GerenciamentoBaseEvento.gbank_05_obter_metadados_arquivo_excluido import obter_metadados_arquivo_excluido
from Observador.GerenciamentoBaseEvento.gbank_06_registrar_evento_no_banco import registrar_evento_no_banco
from Observador.GerenciamentoBaseEvento.gbank_07_atualizar_interface_apos_evento import _atualizar_interface_apos_evento
from Observador.GerenciamentoBaseEvento.gbank_08_scan_directory import scan_directory
from Observador.GerenciamentoBaseEvento.gbank_09_get_tipo_from_snapshot import get_tipo_from_snapshot
from Observador.GerenciamentoBaseEvento.gbank_10_is_directory import is_directory
from Observador.GerenciamentoBaseEvento.gbank_11_limpar_registros import limpar_registros
from Observador.GerenciamentoBaseEvento.gbank_12_obter_tipo_anterior import obter_tipo_anterior
from Observador.GerenciamentoBaseEvento.gbank_13_notificar_evento import notificar_evento
from Observador.GerenciamentoBaseEvento.gbank_14_remover_exclusao_temporaria import _remover_exclusao_temporaria
from Observador.GerenciamentoBaseEvento.gbank_15_criar_evento_exclusao import _criar_evento_exclusao
from Observador.GerenciamentoBaseEvento.gbank_16_criar_evento_padrao import _criar_evento_padrao
from Observador.GerenciamentoBaseEvento.gbank_17_atualizar_interface_apos_exclusao import _atualizar_interface_apos_exclusao
from Observador.GerenciamentoBaseEvento.gbank_18_processar_eventos_movimentacao import processar_eventos_movimentacao
from Observador.GerenciamentoBaseEvento.gbank_19_inserir_evento_movido import _inserir_evento_movido

def obter_caminho_persistente():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)

    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_dir = os.path.join(base_path, "config")

    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)

        except Exception as e:
            print(f"Erro ao criar diretório de configuração: {e}")

    return config_dir


class BaseEvento:
    def __init__(self, observador):
        self.observador = observador
        self.db_path = os.path.join(obter_caminho_persistente(), "monitoramento.db")
        print(f"Caminho do banco de dados: {self.db_path}")

        self.criar_banco_de_dados()

        self.operacoes = {
            self.observador.loc.get_text("op_renamed"): self.observador.loc.get_text("op_renamed"),
            self.observador.loc.get_text("op_added"): self.observador.loc.get_text("op_added"),
            self.observador.loc.get_text("op_deleted"): self.observador.loc.get_text("op_deleted"),
            self.observador.loc.get_text("op_modified"): self.observador.loc.get_text("op_modified"),
            self.observador.loc.get_text("op_moved"): self.observador.loc.get_text("op_moved"),
            self.observador.loc.get_text("op_scanned"): self.observador.loc.get_text("op_scanned")
        }

        self.eventos_excluidos = 0
        self.callback = None

    set_callback = set_callback
    criar_banco_de_dados = criar_banco_de_dados
    processar_exclusao = processar_exclusao
    registrar_evento_especifico = registrar_evento_especifico
    obter_metadados_arquivo_excluido = obter_metadados_arquivo_excluido
    registrar_evento_no_banco = registrar_evento_no_banco
    _atualizar_interface_apos_evento = _atualizar_interface_apos_evento
    scan_directory = scan_directory
    get_tipo_from_snapshot = get_tipo_from_snapshot
    is_directory = is_directory
    limpar_registros = limpar_registros
    obter_tipo_anterior = obter_tipo_anterior
    notificar_evento = notificar_evento
    _remover_exclusao_temporaria = _remover_exclusao_temporaria
    _criar_evento_exclusao = _criar_evento_exclusao
    _criar_evento_padrao = _criar_evento_padrao
    _atualizar_interface_apos_exclusao = _atualizar_interface_apos_exclusao
    processar_eventos_movimentacao = processar_eventos_movimentacao
    _inserir_evento_movido = _inserir_evento_movido
