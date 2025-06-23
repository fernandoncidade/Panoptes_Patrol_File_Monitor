import os
import time
import sqlite3
from PySide6.QtCore import QMutexLocker, QTimer, QObject, Signal, QMutex
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QTableWidgetItem, QApplication


class EventoMovido(QObject):
    evento_processado = Signal(dict)

    def __init__(self):
        super().__init__()

    def processar_evento(self, evento):
        self.evento_processado.emit(evento)

def normalizar_caminho(caminho):
    return os.path.normpath(caminho).replace('/', '\\')

def verificar_movimentacao(interfaceMonitor, evento):
    try:
        if not isinstance(evento, dict) or "tipo_operacao" not in evento or "nome" not in evento:
            print("Evento inválido recebido:", evento)
            return evento

        if "dir_atual" in evento and evento["dir_atual"]:
            evento["dir_atual"] = normalizar_caminho(evento["dir_atual"])

        if "dir_anterior" in evento and evento["dir_anterior"]:
            evento["dir_anterior"] = normalizar_caminho(evento["dir_anterior"])

        with QMutexLocker(interfaceMonitor.mutex):
            if evento["tipo_operacao"] == interfaceMonitor.loc.get_text("op_deleted"):
                evento["exclusao_id"] = str(time.time())
                interfaceMonitor.excluidos_recentemente.setdefault(evento["nome"], []).append(
                    (time.time(), evento.get("dir_anterior", ""), evento)
                )
                evento["_temporario"] = True
                return None

            elif evento["tipo_operacao"] == interfaceMonitor.loc.get_text("op_added"):
                if evento["nome"] in interfaceMonitor.excluidos_recentemente:
                    lista_exclusoes = interfaceMonitor.excluidos_recentemente[evento["nome"]]
                    lista_exclusoes.sort(key=lambda x: x[0], reverse=True)

                    for exclusao in lista_exclusoes:
                        excl_time, excl_dir, evento_exclusao = exclusao
                        if time.time() - excl_time < 3:
                            if excl_dir != evento["dir_atual"]:
                                lista_exclusoes.remove(exclusao)
                                if not lista_exclusoes:
                                    del interfaceMonitor.excluidos_recentemente[evento["nome"]]

                                exclusao_id = evento_exclusao.get("exclusao_id")
                                _remover_exclusao(interfaceMonitor, evento["nome"], excl_dir, exclusao_id)

                                evento["tipo_operacao"] = interfaceMonitor.loc.get_text("op_moved")
                                evento["dir_anterior"] = excl_dir
                                return evento

                    if not lista_exclusoes:
                        del interfaceMonitor.excluidos_recentemente[evento["nome"]]

        return evento

    except Exception as e:
        print(f"Erro geral em verificar_movimentacao: {e}")
        import traceback
        traceback.print_exc()
        return evento

def _remover_exclusao(interfaceMonitor, nome, dir_anterior, exclusao_id=None):
    try:
        with sqlite3.connect(interfaceMonitor.evento_base.db_path) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("BEGIN IMMEDIATE TRANSACTION")

                if exclusao_id:
                    cursor.execute("""
                        SELECT id FROM monitoramento 
                        WHERE tipo_operacao = ? AND nome = ? AND dir_anterior = ?
                        ORDER BY id DESC LIMIT 1
                    """, (interfaceMonitor.loc.get_text("op_deleted"), nome, dir_anterior))

                    resultado = cursor.fetchone()
                    if resultado:
                        registro_id = resultado[0]

                        cursor.execute("""
                            DELETE FROM monitoramento 
                            WHERE id = ?
                        """, (registro_id,))

                        cursor.execute("""
                            DELETE FROM excluido 
                            WHERE tipo_operacao = ? AND nome = ? AND dir_anterior = ?
                            AND timestamp = (SELECT timestamp FROM monitoramento WHERE id = ?)
                        """, (interfaceMonitor.loc.get_text("op_deleted"), nome, dir_anterior, registro_id))

                else:
                    cursor.execute("""
                        DELETE FROM monitoramento 
                        WHERE id IN (
                            SELECT id FROM monitoramento
                            WHERE tipo_operacao = ? AND nome = ? AND dir_anterior = ?
                            ORDER BY id DESC LIMIT 1
                        )
                    """, (interfaceMonitor.loc.get_text("op_deleted"), nome, dir_anterior))

                    cursor.execute("""
                        DELETE FROM excluido 
                        WHERE id IN (
                            SELECT id FROM excluido
                            WHERE tipo_operacao = ? AND nome = ? AND dir_anterior = ?
                            ORDER BY id DESC LIMIT 1
                        )
                    """, (interfaceMonitor.loc.get_text("op_deleted"), nome, dir_anterior))

                cursor.execute("COMMIT")

            except sqlite3.Error as e:
                cursor.execute("ROLLBACK")
                print(f"Erro SQL ao remover exclusão: {e}")
                return False

        _atualizar_tabela_completa(interfaceMonitor)

        return True

    except Exception as e:
        print(f"Erro ao remover registro de exclusão: {e}")
        return False

def _atualizar_tabela_completa(interfaceMonitor):
    try:
        if hasattr(interfaceMonitor, 'gerenciador_tabela'):
            sorting_enabled = interfaceMonitor.tabela_dados.isSortingEnabled()
            interfaceMonitor.tabela_dados.setSortingEnabled(False)
            interfaceMonitor.gerenciador_tabela.atualizar_dados_tabela(interfaceMonitor.tabela_dados)

            _atualizar_contador_eventos(interfaceMonitor)
            interfaceMonitor.atualizar_status()

            interfaceMonitor.tabela_dados.setSortingEnabled(sorting_enabled)
            interfaceMonitor.tabela_dados.viewport().update()

    except Exception as e:
        print(f"Erro ao atualizar tabela completa: {e}")
        import traceback
        traceback.print_exc()

def _atualizar_contador_eventos(interfaceMonitor):
    try:
        row_count = interfaceMonitor.tabela_dados.rowCount()

        excluidos = 0
        if hasattr(interfaceMonitor, 'evento_base') and hasattr(interfaceMonitor.evento_base, 'eventos_excluidos'):
            excluidos = interfaceMonitor.evento_base.eventos_excluidos

        total_eventos = row_count + excluidos

        if not hasattr(interfaceMonitor, 'contador_eventos'):
            interfaceMonitor.contador_eventos = 0

        if interfaceMonitor.contador_eventos != total_eventos:
            interfaceMonitor.contador_eventos = total_eventos

        if hasattr(interfaceMonitor, 'rotulo_contador_eventos'):
            interfaceMonitor.rotulo_contador_eventos.setText(f"{interfaceMonitor.loc.get_text('events_monitored')}: {interfaceMonitor.contador_eventos}")

        interfaceMonitor.ultimo_update_status = time.time()

    except Exception as e:
        print(f"Erro ao atualizar contador de eventos: {e}")
        import traceback
        traceback.print_exc()

def _inicializar_sistema_evento(interfaceMonitor):
    if not hasattr(interfaceMonitor, 'processador_evento'):
        interfaceMonitor.processador_evento = EventoMovido()

        if not hasattr(interfaceMonitor, 'evento_buffer'):
            interfaceMonitor.evento_buffer = EventoBuffer(interfaceMonitor)

        if not hasattr(interfaceMonitor, 'movimentacao_worker'):
            from Observador.ob_09_MovimentacaoWorker import MovimentacaoWorker
            interfaceMonitor.movimentacao_worker = MovimentacaoWorker(interfaceMonitor)
            interfaceMonitor.movimentacao_worker.processamento_concluido.connect(lambda: interfaceMonitor.gerenciador_tabela.atualizar_dados_tabela(interfaceMonitor.tabela_dados))

        interfaceMonitor.processador_evento.evento_processado.connect(lambda evento: interfaceMonitor.evento_buffer.adicionar_evento(evento))

    if not hasattr(interfaceMonitor, 'contador_eventos'):
        interfaceMonitor.contador_eventos = 0

    if not hasattr(interfaceMonitor, 'refresh_timer'):
        interfaceMonitor.refresh_timer = QTimer()
        interfaceMonitor.refresh_timer.timeout.connect(lambda: _sincronizar_e_atualizar_status(interfaceMonitor))
        interfaceMonitor.refresh_timer.start(2000)

    if not hasattr(interfaceMonitor, 'exclusao_timer'):
        interfaceMonitor.exclusao_timer = QTimer()
        interfaceMonitor.exclusao_timer.timeout.connect(lambda: _processar_exclusoes_pendentes(interfaceMonitor))
        interfaceMonitor.exclusao_timer.start(3000)

def _processar_exclusoes_pendentes(interfaceMonitor):
    try:
        eventos_para_processar = []
        tempo_atual = time.time()

        with QMutexLocker(interfaceMonitor.mutex):
            nomes_para_remover = []
            for nome, eventos_lista in interfaceMonitor.excluidos_recentemente.items():
                eventos_a_remover = []
                for registro in eventos_lista:
                    timestamp, dir_anterior, evento = registro
                    if tempo_atual - timestamp > 3:
                        novo_evento = evento.copy()
                        novo_evento.pop("_temporario", None)
                        novo_evento["id_exclusao_unico"] = f"{nome}_{timestamp}_{id(registro)}"
                        eventos_para_processar.append(novo_evento)
                        eventos_a_remover.append(registro)

                for registro in eventos_a_remover:
                    eventos_lista.remove(registro)

                if not eventos_lista:
                    nomes_para_remover.append(nome)

            for nome in nomes_para_remover:
                del interfaceMonitor.excluidos_recentemente[nome]

        for evento in eventos_para_processar:
            QTimer.singleShot(0, lambda e=evento: interfaceMonitor.processador_evento.evento_processado.emit(e))

    except Exception as e:
        print(f"Erro ao processar exclusões pendentes: {e}")
        import traceback
        traceback.print_exc()

def _sincronizar_e_atualizar_status(interfaceMonitor):
    _atualizar_contador_eventos(interfaceMonitor)
    interfaceMonitor.atualizar_status()

def _adicionar_item_tabela(interfaceMonitor, evento, atualizar_interface=True):
    try:
        tipo_operacao_traduzido = interfaceMonitor.loc.get_text(evento["tipo_operacao"])
        if not interfaceMonitor.painel_filtros.verificar_filtro_operacao(tipo_operacao_traduzido):
            return

        row_position = 0
        interfaceMonitor.tabela_dados.insertRow(row_position)

        colunas_visiveis = [(key, col) for key, col in sorted(interfaceMonitor.gerenciador_colunas.COLUNAS_DISPONIVEIS.items(), key=lambda x: x[1]["ordem"]) if col["visivel"]]

        cores = {
            interfaceMonitor.loc.get_text("op_renamed"): QColor(0, 255, 0),
            interfaceMonitor.loc.get_text("op_added"): QColor(0, 0, 255),
            interfaceMonitor.loc.get_text("op_deleted"): QColor(255, 0, 0),
            interfaceMonitor.loc.get_text("op_modified"): QColor(255, 98, 0),
            interfaceMonitor.loc.get_text("op_moved"): QColor(255, 0, 255),
            interfaceMonitor.loc.get_text("op_scanned"): QColor(128, 128, 128)
        }

        for col, (key, coluna) in enumerate(colunas_visiveis):
            try:
                valor = coluna["getter"](evento) if callable(coluna.get("getter")) else evento.get(key, "")

                if key == "tipo_operacao":
                    valor = interfaceMonitor.loc.get_text(valor)

                if key in ["dir_anterior", "dir_atual"] and valor:
                    valor = "" if not valor or valor == "." else normalizar_caminho(str(valor))

                valor_texto = str(valor)
                novo_item = QTableWidgetItem(valor_texto)

                if key == "tipo_operacao":
                    novo_item.setBackground(cores.get(valor, QColor(255, 255, 255)))

                interfaceMonitor.tabela_dados.setItem(row_position, col, novo_item)

            except Exception as e:
                print(f"Erro ao adicionar item na coluna {key}: {e}")
                interfaceMonitor.tabela_dados.setItem(row_position, col, QTableWidgetItem(""))

        if atualizar_interface:
            _atualizar_contador_eventos(interfaceMonitor)
            interfaceMonitor.atualizar_status()

    except Exception as e:
        print(f"Erro ao adicionar item na tabela: {e}")
        import traceback
        traceback.print_exc()

def adicionar_evento(interfaceMonitor, evento):
    try:
        if not evento or "tipo_operacao" not in evento or "nome" not in evento:
            print("Evento inválido recebido:", evento)
            return

        _inicializar_sistema_evento(interfaceMonitor)

        evento_processado = verificar_movimentacao(interfaceMonitor, evento)

        if evento_processado is not None:
            interfaceMonitor.processador_evento.evento_processado.emit(evento_processado)

    except Exception as e:
        print(f"Erro em adicionar_evento: {e}")
        import traceback
        traceback.print_exc()

class EventoBuffer:
    def __init__(self, interface_monitor):
        self.interface = interface_monitor
        self.lock = QMutex()
        self.ultimo_update = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_interface)
        self.timer.start(500)

    def adicionar_evento(self, evento):
        with QMutexLocker(self.lock):
            self._processar_evento_imediato(evento)

    def _processar_evento_imediato(self, evento):
        ordenacao_habilitada = self.interface.tabela_dados.isSortingEnabled()
        self.interface.tabela_dados.setSortingEnabled(False)

        try:
            _adicionar_item_tabela(self.interface, evento, atualizar_interface=False)

            if evento.get("tipo_operacao") == self.interface.loc.get_text("op_moved") and hasattr(self.interface, 'movimentacao_worker'):
                self.interface.movimentacao_worker.adicionar_evento(evento)

        finally:
            self.interface.tabela_dados.setSortingEnabled(ordenacao_habilitada)
            self.interface.tabela_dados.viewport().update()
            QApplication.processEvents()

    def atualizar_interface(self):
        _atualizar_contador_eventos(self.interface)
        self.interface.atualizar_status()

        if hasattr(self.interface, 'gerenciador_tabela'):
            self.interface.gerenciador_tabela.atualizacao_pendente = True

        self.interface.tabela_dados.viewport().update()
