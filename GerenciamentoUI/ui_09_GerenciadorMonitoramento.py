import os
import gc
from utils.LogManager import LogManager
import sqlite3
from PySide6.QtCore import QMutexLocker
from PySide6.QtWidgets import QApplication

logger = LogManager.get_logger()


class GerenciadorMonitoramento:
    def __init__(self, interface_principal):
        self.interface = interface_principal

    def reiniciar_sistema_monitoramento(self):
        try:
            logger.info("Reiniciando sistema de monitoramento completo")

            rows_antes = self.interface.tabela_dados.rowCount()
            logger.info(f"Eventos exibidos antes do reinício: {rows_antes}")

            if hasattr(self.interface, 'observador') and self.interface.observador:
                self.interface.observador.parar()
                self.interface.observador = None

            if hasattr(self.interface, 'refresh_timer'):
                self.interface.refresh_timer.stop()
                self.interface.refresh_timer.timeout.disconnect()

            if hasattr(self.interface, 'exclusao_timer'):
                self.interface.exclusao_timer.stop()
                self.interface.exclusao_timer.timeout.disconnect()

            self.interface.excluidos_recentemente.clear()

            if hasattr(self.interface, 'processador_evento'):
                try:
                    self.interface.processador_evento.evento_processado.disconnect()

                except:
                    pass

                self.interface.processador_evento = None

            if hasattr(self.interface, 'evento_base'):
                with sqlite3.connect(self.interface.evento_base.db_path) as conn:
                    conn.execute("PRAGMA optimize")
                    conn.execute("VACUUM")

                    cursor = conn.cursor()
                    count = cursor.execute("SELECT COUNT(*) FROM monitoramento").fetchone()[0]
                    logger.info(f"Total de eventos no banco de dados: {count}")

            if hasattr(self.interface, 'gerenciador_colunas') and hasattr(self.interface.gerenciador_colunas, 'cache_metadados'):
                self.interface.gerenciador_colunas.cache_metadados.clear()

            if hasattr(self.interface, 'evento_buffer'):
                with QMutexLocker(self.interface.evento_buffer.lock):
                    self.interface.evento_buffer.eventos.clear()

                self.interface.evento_buffer.timer.stop()
                self.interface.evento_buffer.timer = None
                self.interface.evento_buffer = None

            gc.collect()

            logger.info("Recarregando dados da tabela após reinício do sistema")
            if hasattr(self.interface, 'evento_base'):
                if hasattr(self.interface, 'painel_filtros'):
                    filtros_estado = {}
                    for op, checkbox in self.interface.painel_filtros.checkboxes_operacao.items():
                        filtros_estado[op] = checkbox.isChecked()

                self.interface.tabela_dados.clearContents()
                self.interface.tabela_dados.setRowCount(0)

                with sqlite3.connect(self.interface.evento_base.db_path) as conn:
                    cursor = conn.cursor()
                    registros = cursor.execute("""
                        SELECT id, tipo_operacao, dir_atual, dir_anterior, timestamp, nome 
                        FROM monitoramento ORDER BY id
                    """).fetchall()

                    for registro in registros:
                        evento = {
                            'id': registro[0],
                            'tipo_operacao': registro[1],
                            'caminho': registro[2],
                            'caminho_antigo': registro[3],
                            'data': registro[4],
                            'arquivo': registro[5] or os.path.basename(registro[2] or registro[3] or "")
                        }
                        self.interface.adicionar_evento(evento)

                if hasattr(self.interface, 'painel_filtros') and hasattr(self.interface.painel_filtros, 'administrador_filtros'):
                    self.interface.painel_filtros.administrador_filtros.aplicar_filtros()

            logger.info("Sistema de monitoramento reiniciado com sucesso")
            rows_depois = self.interface.tabela_dados.rowCount()
            logger.info(f"Eventos exibidos após recarga: {rows_depois}")
            QApplication.processEvents()

        except Exception as e:
            logger.error(f"Erro ao reiniciar sistema de monitoramento: {e}", exc_info=True)
