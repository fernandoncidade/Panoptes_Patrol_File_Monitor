import os
import sys
from utils.LogManager import LogManager
import subprocess
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMessageBox, QApplication, QDialog
from Filtros.fil_01_Filtros import Filtros

logger = LogManager.get_logger()


class GerenciadorEventosUI:
    def __init__(self, interface_principal):
        self.interface = interface_principal
        self.loc = interface_principal.loc

    def alternar_filtro(self):
        try:
            acao = self.interface.sender()

            if acao and isinstance(acao, QAction):
                filtro = acao.data()
                esta_marcado = acao.isChecked()

                if (hasattr(self.interface, 'painel_filtros') and 
                    hasattr(self.interface.painel_filtros, 'checkboxes_operacao') and
                    filtro in self.interface.painel_filtros.checkboxes_operacao):

                    checkbox = self.interface.painel_filtros.checkboxes_operacao[filtro]
                    checkbox.blockSignals(True)
                    checkbox.setChecked(esta_marcado)
                    checkbox.blockSignals(False)

                for widget in QApplication.topLevelWidgets():
                    if isinstance(widget, QDialog) and hasattr(widget, 'findChild'):
                        for painel_filtro in widget.findChildren(Filtros):
                            if (hasattr(painel_filtro, 'checkboxes_operacao') and 
                                filtro in painel_filtro.checkboxes_operacao):
                                painel_filtro.checkboxes_operacao[filtro].blockSignals(True)
                                painel_filtro.checkboxes_operacao[filtro].setChecked(esta_marcado)
                                painel_filtro.checkboxes_operacao[filtro].blockSignals(False)
                                painel_filtro.administrador_filtros.aplicar_filtros()

                chave_para_operacao = {
                    "op_moved": self.loc.get_text("op_moved"),
                    "op_renamed": self.loc.get_text("op_renamed"),
                    "op_added": self.loc.get_text("op_added"),
                    "op_deleted": self.loc.get_text("op_deleted"),
                    "op_modified": self.loc.get_text("op_modified"),
                    "op_scanned": self.loc.get_text("op_scanned")
                }

                for row in range(self.interface.tabela_dados.rowCount()):
                    tipo_op_cell = self.interface.tabela_dados.item(row, 0)
                    if tipo_op_cell:
                        tipo_op_texto = tipo_op_cell.text()

                        if tipo_op_texto == chave_para_operacao.get(filtro):
                            self.interface.tabela_dados.setRowHidden(row, not esta_marcado)

                self.interface.atualizar_status()
                logger.debug(f"Filtro '{filtro}' alterado para {esta_marcado}")

        except Exception as e:
            logger.error(f"Erro ao alternar filtro: {e}", exc_info=True)

    def alternar_visibilidade_coluna(self):
        try:
            acao = self.interface.sender()

            if acao and isinstance(acao, QAction):
                chave_coluna = acao.data()

                if chave_coluna in self.interface.gerenciador_colunas.COLUNAS_DISPONIVEIS:
                    visivel = acao.isChecked()
                    self.interface.gerenciador_colunas.COLUNAS_DISPONIVEIS[chave_coluna]["visivel"] = visivel
                    self.interface.gerenciador_colunas.salvar_configuracoes()
                    self.interface.gerenciador_colunas.configurar_tabela(self.interface.tabela_dados)

        except Exception as e:
            logger.error(f"Erro ao alternar visibilidade da coluna: {e}", exc_info=True)

    def resetar_colunas(self):
        try:
            logger.info("Iniciando reset das colunas para configuração padrão")

            colunas_padrao = {
                "tipo_operacao": True,
                "nome": True,
                "dir_anterior": True,
                "dir_atual": True,
                "data_criacao": False,
                "data_modificacao": True,
                "data_acesso": False,
                "tipo": True,
                "tamanho": False,
                "atributos": False,
                "autor": False,
                "dimensoes": False,
                "duracao": False,
                "taxa_bits": False,
                "protegido": False,
                "paginas": False,
                "linhas": False,
                "palavras": False,
                "paginas_estimadas": False,
                "linhas_codigo": False,
                "total_linhas": False,
                "slides_estimados": False,
                "arquivos": False,
                "descompactados": False,
                "slides": False,
                "binario": False,
                "planilhas": False,
                "colunas": False,
                "registros": False,
                "tabelas": False
            }

            for coluna, visivel in colunas_padrao.items():
                if coluna in self.interface.gerenciador_colunas.COLUNAS_DISPONIVEIS:
                    self.interface.gerenciador_colunas.COLUNAS_DISPONIVEIS[coluna]["visivel"] = visivel

            if hasattr(self.interface, 'gerenciador_menus_ui') and hasattr(self.interface.gerenciador_menus_ui, 'acoes_colunas'):
                for coluna, acao in self.interface.gerenciador_menus_ui.acoes_colunas.items():
                    if coluna in colunas_padrao:
                        acao.setChecked(colunas_padrao[coluna])
                        logger.debug(f"Coluna {coluna} definida como {colunas_padrao[coluna]}")

                    else:
                        acao.setChecked(False)
                        logger.debug(f"Coluna {coluna} definida como False (não está nas colunas padrão)")

            self.interface.gerenciador_colunas.salvar_configuracoes()
            self.interface.gerenciador_colunas.configurar_tabela(self.interface.tabela_dados)

            logger.info("Reset de colunas concluído com sucesso")
            QMessageBox.information(self.interface, self.loc.get_text("success"), self.loc.get_text("columns_reset_success"))

        except Exception as e:
            logger.error(f"Erro ao resetar colunas: {e}", exc_info=True)
            QMessageBox.warning(self.interface, self.loc.get_text("error"), self.loc.get_text("columns_reset_error").format(str(e)))

    def alterar_idioma(self):
        try:
            acao = self.interface.sender()
            if acao and isinstance(acao, QAction):
                novo_idioma = acao.data()

                if novo_idioma != self.loc.idioma_atual:
                    resposta = self._confirmar_mudanca_idioma()

                    if resposta == QMessageBox.Yes:
                        idioma_anterior = self.loc.idioma_atual
                        self.loc.set_idioma(novo_idioma)

                        self.interface.atualizar_interface()

                        if hasattr(self.interface, 'gerenciador_tabela') and hasattr(self.interface, 'tabela_dados'):
                            self.interface.gerenciador_tabela.atualizar_dados_tabela(self.interface.tabela_dados)

                        from PySide6.QtWidgets import QApplication, QDialog
                        for widget in QApplication.topLevelWidgets():
                            if isinstance(widget, QDialog) and widget.windowTitle() == self.loc.get_text("statistics"):
                                if hasattr(self.interface, 'gerenciador_estatisticas_ui'):
                                    self.interface.gerenciador_estatisticas_ui._atualizar_graficos(widget)

                        logger.info(f"Idioma alterado de {idioma_anterior} para {novo_idioma} sem reiniciar")

                        QMessageBox.information(self.interface, self.loc.get_text("success"), self.loc.get_text("language_changed_success"))

                    else:
                        for acao in self.interface.findChildren(QAction):
                            if hasattr(acao, 'data') and callable(acao.data) and acao.data() == self.loc.idioma_atual:
                                acao.setChecked(True)

        except Exception as e:
            logger.error(f"Erro ao alterar idioma: {e}", exc_info=True)
            QMessageBox.warning(self.interface, self.loc.get_text("error"), self.loc.get_text("language_change_error").format(str(e)))

    def _confirmar_mudanca_idioma(self):
        message_box = QMessageBox(self.interface)
        message_box.setIcon(QMessageBox.Warning)
        message_box.setWindowTitle(self.loc.get_text("warning"))
        message_box.setText(self.loc.get_text("language_change_confirm"))

        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setDefaultButton(QMessageBox.No)

        message_box.setButtonText(QMessageBox.Yes, self.loc.get_text("yes"))
        message_box.setButtonText(QMessageBox.No, self.loc.get_text("no"))

        return message_box.exec()

    def _limpar_dados_monitorados(self):
        try:
            logger.info("Iniciando limpeza de dados para reinício da aplicação")

            if hasattr(self.interface, 'observador') and self.interface.observador and self.interface.observador.ativo:
                logger.debug("Desativando monitoramento antes de reiniciar")
                self.interface.gerenciador_botoes.alternar_analise_diretorio()

            if hasattr(self.interface, 'evento_base'):
                logger.debug("Chamando método limpar_registros() do evento_base")
                self.interface.evento_base.limpar_registros()

            db_paths = [
                "monitoramento.db", 
                os.path.join(os.path.dirname(__file__), "..", "Observador", "monitoramento.db"), 
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Observador", "monitoramento.db")
            ]

            db_removido = False
            for db_path in db_paths:
                if os.path.exists(db_path):
                    os.remove(db_path)
                    logger.info(f"Arquivo de banco de dados removido: {db_path}")
                    db_removido = True

            if not db_removido:
                logger.warning("Arquivo de banco de dados não encontrado para remoção.")

            self._limpar_dados_interface()

            logger.info("Limpeza de dados para reinício concluída")

        except Exception as e:
            logger.error(f"Erro ao limpar dados monitorados: {e}", exc_info=True)

    def _limpar_dados_interface(self):
        try:
            logger.info("Iniciando limpeza da interface para reinício")

            if hasattr(self.interface, 'tabela_dados'):
                self.interface.tabela_dados.clearContents()
                self.interface.tabela_dados.setRowCount(0)
                self.interface.tabela_dados.viewport().update()
                logger.debug("Tabela de dados limpa")

            if (hasattr(self.interface, 'gerenciador_colunas') and 
                hasattr(self.interface.gerenciador_colunas, 'cache_metadados')):
                self.interface.gerenciador_colunas.cache_metadados.clear()
                logger.debug("Cache de metadados limpo")

            if (hasattr(self.interface, 'painel_filtros') and 
                hasattr(self.interface.painel_filtros, 'administrador_filtros')):
                self.interface.painel_filtros.administrador_filtros.limpar_filtros()
                logger.debug("Filtros limpos")

            if hasattr(self.interface, 'ultimo_salvamento'):
                self.interface.ultimo_salvamento = None
                logger.debug("Último salvamento resetado")

            if hasattr(self.interface, 'diretorio_atual'):
                self.interface.diretorio_atual = None
                logger.debug("Diretório atual resetado")

            if hasattr(self.interface, 'excluidos_recentemente'):
                self.interface.excluidos_recentemente.clear()
                logger.debug("Lista de excluídos recentemente limpa")

            if hasattr(self.interface, 'atualizar_status'):
                self.interface.atualizar_status()

            logger.info("Interface limpa com sucesso para reinício")

        except Exception as e:
            logger.error(f"Erro ao limpar interface: {e}", exc_info=True)

    def _reiniciar_aplicativo(self):
        try:
            if hasattr(self.interface, 'rotulo_resultado'):
                self.interface.rotulo_resultado.setText(
                    self.loc.get_text("language_change_confirm").split('?')[0] + "..."
                )

            from PySide6.QtCore import QCoreApplication, QTimer
            QCoreApplication.processEvents()

            self._limpar_dados_monitorados()

            def executar_reinicio():
                try:
                    python = sys.executable
                    script_path = sys.argv[0]
                    args = sys.argv[1:]

                    logger.info(f"Reiniciando aplicativo para aplicar novo idioma: {self.loc.idioma_atual}")

                    subprocess.Popen([python, script_path] + args)
                    sys.exit(0)

                except Exception as e:
                    logger.error(f"Erro no timer de reinício: {e}", exc_info=True)

            QTimer.singleShot(500, executar_reinicio)

        except Exception as e:
            logger.error(f"Erro ao reiniciar aplicativo: {e}", exc_info=True)
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self.interface, self.loc.get_text("error"), self.loc.get_text("restart_error").format(str(e)))
