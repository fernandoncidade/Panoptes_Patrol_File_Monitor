import os
from datetime import datetime
from PySide6.QtCore import QDateTime
from PySide6.QtGui import QAction
from utils.LogManager import LogManager

logger = LogManager.get_logger()


class AdministradorFiltros:
    filtros_estado = {
        "ignorar_mover": True,
        "ignorar_renomeados": True,
        "ignorar_adicionados": True,
        "ignorar_excluidos": True,
        "ignorar_data_modificados": True,
        "ignorar_escaneados": True
    }

    def __init__(self, parent):
        logger.debug("Inicializando AdministradorFiltros")
        self.parent = parent
        self.contadores = {
            "op_moved": 0,
            "op_renamed": 0, 
            "op_added": 0,
            "op_deleted": 0,
            "op_modified": 0,
            "op_scanned": 0
        }
        self.contadores_originais = {
            "op_moved": 0,
            "op_renamed": 0, 
            "op_added": 0,
            "op_deleted": 0,
            "op_modified": 0,
            "op_scanned": 0
        }

        from PySide6.QtWidgets import QApplication
        for widget in QApplication.topLevelWidgets():
            if hasattr(widget, 'loc') and hasattr(widget.loc, 'idioma_alterado'):
                widget.loc.idioma_alterado.connect(self.atualizar_contagem_apos_idioma)
                logger.debug("Conectado sinal de idioma alterado da janela principal")
                break

        if hasattr(self.parent, 'loc') and hasattr(self.parent.loc, 'idioma_alterado'):
            self.parent.loc.idioma_alterado.connect(self.atualizar_contagem_apos_idioma)
            logger.debug("Conectado sinal de idioma alterado do componente pai")

    def aplicar_filtros(self):
        try:
            logger.debug("Aplicando filtros")
            self.salvar_estado_checkboxes()

            for chave in self.contadores:
                self.contadores[chave] = 0
                self.contadores_originais[chave] = 0

            texto_busca = self.parent.campo_busca.text().lower()
            extensoes = [ext.strip().lower() for ext in self.parent.campo_extensao.text().split(',') if ext.strip()]
            data_inicial = self.parent.data_inicial.dateTime().toPython()
            data_final = self.parent.data_final.dateTime().toPython()

            from PySide6.QtWidgets import QApplication
            main_window = None
            gerenciador_colunas = None

            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'gerenciador_colunas'):
                    main_window = widget
                    gerenciador_colunas = widget.gerenciador_colunas
                    break

            tabela = self.parent.tabela_dados

            indices_colunas = {}

            if gerenciador_colunas and hasattr(gerenciador_colunas, 'COLUNAS_DISPONIVEIS'):
                colunas_visiveis = [(key, col) for key, col in sorted(
                    gerenciador_colunas.COLUNAS_DISPONIVEIS.items(), 
                    key=lambda x: x[1]["ordem"]) if col["visivel"]]

                indices_colunas = {key: idx for idx, (key, _) in enumerate(colunas_visiveis)}
                logger.debug(f"Índices de colunas obtidos do gerenciador: {indices_colunas}")

            else:
                num_colunas = tabela.columnCount()

                for col in range(num_colunas):
                    header_item = tabela.horizontalHeaderItem(col)
                    if header_item:
                        header_text = header_item.text().lower()

                        if "operação" in header_text or "operacao" in header_text:
                            indices_colunas["tipo_operacao"] = col

                        elif "nome" in header_text:
                            indices_colunas["nome"] = col

                        elif "anterior" in header_text:
                            indices_colunas["dir_anterior"] = col

                        elif "atual" in header_text:
                            indices_colunas["dir_atual"] = col

                        elif "modif" in header_text:
                            indices_colunas["data_modificacao"] = col

                        elif "cria" in header_text:
                            indices_colunas["data_criacao"] = col

                if "tipo_operacao" not in indices_colunas:
                    indices_colunas["tipo_operacao"] = 0

                if "nome" not in indices_colunas:
                    indices_colunas["nome"] = 1

                if "dir_anterior" not in indices_colunas:
                    indices_colunas["dir_anterior"] = 2

                if "dir_atual" not in indices_colunas:
                    indices_colunas["dir_atual"] = 3

                logger.debug(f"Índices de colunas inferidos dos cabeçalhos: {indices_colunas}")

            operacao_para_chave = {
                self.parent.loc.get_text("op_moved"): "op_moved",
                self.parent.loc.get_text("op_renamed"): "op_renamed",
                self.parent.loc.get_text("op_added"): "op_added", 
                self.parent.loc.get_text("op_deleted"): "op_deleted",
                self.parent.loc.get_text("op_modified"): "op_modified",
                self.parent.loc.get_text("op_scanned"): "op_scanned"
            }

            for row in range(tabela.rowCount()):
                tipo_op_item = tabela.item(row, indices_colunas.get("tipo_operacao", 0))
                if tipo_op_item:
                    tipo_op = tipo_op_item.text()
                    chave_operacao = operacao_para_chave.get(tipo_op)
                    if chave_operacao in self.contadores_originais:
                        self.contadores_originais[chave_operacao] += 1

            logger.debug(f"Total original por tipo: {self.contadores_originais}")

            for row in range(tabela.rowCount()):
                mostrar = True
                tipo_op = None

                tipo_op_item = tabela.item(row, indices_colunas.get("tipo_operacao", 0))
                if tipo_op_item:
                    tipo_op = tipo_op_item.text()
                    if not self.verificar_filtro_operacao(tipo_op):
                        mostrar = False

                chave_operacao = operacao_para_chave.get(tipo_op)

                if mostrar and texto_busca:
                    texto_encontrado = False
                    campos_busca = ["nome", "dir_anterior", "dir_atual"]

                    for campo in campos_busca:
                        if campo in indices_colunas:
                            item = tabela.item(row, indices_colunas[campo])
                            if item and texto_busca in item.text().lower():
                                texto_encontrado = True
                                break

                    if not texto_encontrado:
                        mostrar = False

                if mostrar and extensoes:
                    extensao_encontrada = False

                    nome_item = tabela.item(row, indices_colunas.get("nome", 1))
                    if nome_item:
                        nome_arquivo = nome_item.text()
                        extensao = os.path.splitext(nome_arquivo)[1].lower().lstrip('.')

                        if extensao in extensoes:
                            extensao_encontrada = True

                    if not extensao_encontrada:
                        mostrar = False

                if mostrar:
                    if chave_operacao == "op_moved" and hasattr(self.parent, 'ignorar_mover') and self.parent.ignorar_mover.isChecked():
                        pass

                    elif chave_operacao == "op_renamed" and hasattr(self.parent, 'ignorar_renomeados') and self.parent.ignorar_renomeados.isChecked():
                        pass

                    elif chave_operacao == "op_added" and hasattr(self.parent, 'ignorar_adicionados') and self.parent.ignorar_adicionados.isChecked():
                        pass

                    elif chave_operacao == "op_deleted" and hasattr(self.parent, 'ignorar_excluidos') and self.parent.ignorar_excluidos.isChecked():
                        pass

                    elif chave_operacao == "op_modified" and hasattr(self.parent, 'ignorar_data_modificados') and self.parent.ignorar_data_modificados.isChecked():
                        pass

                    elif chave_operacao == "op_scanned" and hasattr(self.parent, 'ignorar_escaneados') and self.parent.ignorar_escaneados.isChecked():
                        pass

                    elif chave_operacao == "op_moved" or chave_operacao == "op_renamed" or chave_operacao == "op_added" or chave_operacao == "op_deleted" or chave_operacao == "op_modified" or chave_operacao == "op_scanned":
                        data_item = None
                        for campo_data in ["data_modificacao", "data_criacao"]:
                            if campo_data in indices_colunas:
                                data_item = tabela.item(row, indices_colunas[campo_data])
                                if data_item and data_item.text().strip():
                                    break

                        if data_item and data_item.text().strip():
                            try:
                                data_texto = data_item.text().strip()
                                try:
                                    data_evento = datetime.strptime(data_texto, "%Y-%m-%d %H:%M:%S")

                                except ValueError:
                                    try:
                                        data_evento = datetime.strptime(data_texto, "%d/%m/%Y %H:%M:%S")

                                    except ValueError:
                                        data_evento = datetime.strptime(data_texto.split()[0], "%Y-%m-%d")

                                if not (data_inicial <= data_evento <= data_final):
                                    mostrar = False
                                    nome = tabela.item(row, indices_colunas.get("nome", 1)).text() if tabela.item(row, indices_colunas.get("nome", 1)) else "Desconhecido"
                                    logger.debug(f"Arquivo fora do intervalo de datas: {nome}, data: {data_texto}, intervalo: {data_inicial} a {data_final}")

                            except Exception as e:
                                nome = tabela.item(row, indices_colunas.get("nome", 1)).text() if tabela.item(row, indices_colunas.get("nome", 1)) else "Desconhecido"
                                logger.debug(f"Erro ao processar data do arquivo modificado: {nome}, erro: {str(e)}")
                                mostrar = True

                    else:
                        data_item = None
                        for campo_data in ["data_modificacao", "data_criacao"]:
                            if campo_data in indices_colunas:
                                data_item = tabela.item(row, indices_colunas[campo_data])
                                if data_item and data_item.text().strip():
                                    break

                        if data_item and data_item.text().strip():
                            try:
                                data_texto = data_item.text().strip()
                                data_evento = datetime.strptime(data_texto, "%Y-%m-%d %H:%M:%S")

                                if not (data_inicial <= data_evento <= data_final):
                                    mostrar = False

                            except (ValueError, TypeError):
                                nome = tabela.item(row, indices_colunas.get("nome", 1)).text() if tabela.item(row, indices_colunas.get("nome", 1)) else "Desconhecido"
                                logger.debug(f"Formato de data inválido no item {row} (tipo: {tipo_op}, nome: {nome}). Mantendo visível.")
                                mostrar = True

                if mostrar and chave_operacao and chave_operacao in self.contadores:
                    self.contadores[chave_operacao] += 1

                tabela.setRowHidden(row, not mostrar)

            logger.debug(f"Contagem de itens visíveis por tipo após filtragem: {self.contadores}")
            logger.debug(f"Diferença entre original e filtrado: " + ", ".join([f"{k}: {self.contadores_originais[k] - self.contadores[k]}" for k in self.contadores.keys()]))

            self.sincronizar_menu_principal_com_filtros()
            self.parent.filtroAplicado.emit()
            logger.debug("Filtros aplicados com sucesso")

        except Exception as e:
            logger.error(f"Erro ao aplicar filtros: {e}", exc_info=True)
            for row in range(self.parent.tabela_dados.rowCount()):
                self.parent.tabela_dados.setRowHidden(row, False)

    def limpar_filtros(self):
        logger.info("Limpando todos os filtros")
        try:
            for cb in self.parent.checkboxes_operacao.values():
                cb.setChecked(True)

            self.parent.campo_busca.clear()
            self.parent.campo_extensao.clear()
            self.parent.data_inicial.setDateTime(QDateTime.currentDateTime().addDays(-30))
            self.parent.data_final.setDateTime(QDateTime.currentDateTime())

            # Redefinir as checkboxes e atualizar o estado salvo
            if hasattr(self.parent, 'ignorar_mover'):
                self.parent.ignorar_mover.setChecked(True)
                AdministradorFiltros.filtros_estado["ignorar_mover"] = True

            if hasattr(self.parent, 'ignorar_renomeados'):
                self.parent.ignorar_renomeados.setChecked(True)
                AdministradorFiltros.filtros_estado["ignorar_renomeados"] = True

            if hasattr(self.parent, 'ignorar_adicionados'):
                self.parent.ignorar_adicionados.setChecked(True)
                AdministradorFiltros.filtros_estado["ignorar_adicionados"] = True

            if hasattr(self.parent, 'ignorar_excluidos'):
                self.parent.ignorar_excluidos.setChecked(True)
                AdministradorFiltros.filtros_estado["ignorar_excluidos"] = True

            if hasattr(self.parent, 'ignorar_data_modificados'):
                self.parent.ignorar_data_modificados.setChecked(True)
                AdministradorFiltros.filtros_estado["ignorar_data_modificados"] = True

            if hasattr(self.parent, 'ignorar_escaneados'):
                self.parent.ignorar_escaneados.setChecked(True)
                AdministradorFiltros.filtros_estado["ignorar_escaneados"] = True

            for row in range(self.parent.tabela_dados.rowCount()):
                self.parent.tabela_dados.setRowHidden(row, False)

            self.sincronizar_menu_principal_com_filtros()
            self.parent.filtroAplicado.emit()
            logger.debug("Filtros limpos e visualização atualizada")

        except Exception as e:
            logger.error(f"Erro ao limpar filtros: {e}", exc_info=True)

    def sincronizar_menu_principal_com_filtros(self):
        try:
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
                    if action.text() == main_window.loc.get_text("settings"):
                        menu_configuracoes = action.menu()
                        break

                if menu_configuracoes:
                    for action in menu_configuracoes.actions():
                        if action.text() == main_window.loc.get_text("filters"):
                            submenu_filtros = action.menu()
                            break

                if submenu_filtros:
                    for acao in submenu_filtros.actions():
                        if hasattr(acao, 'data') and callable(acao.data):
                            filtro = acao.data()
                            if (isinstance(filtro, str) and 
                                filtro in self.parent.checkboxes_operacao):
                                esta_marcado = self.parent.checkboxes_operacao[filtro].isChecked()
                                acao.blockSignals(True)
                                acao.setChecked(esta_marcado)
                                acao.blockSignals(False)

                    logger.debug("Sincronizado menu principal com filtros (via submenu)")

                else:
                    for acao in main_window.findChildren(QAction):
                        if hasattr(acao, 'data') and callable(acao.data):
                            filtro = acao.data()
                            if (isinstance(filtro, str) and 
                                filtro in self.parent.checkboxes_operacao):
                                esta_marcado = self.parent.checkboxes_operacao[filtro].isChecked()
                                acao.blockSignals(True)
                                acao.setChecked(esta_marcado)
                                acao.blockSignals(False)

                    logger.debug("Sincronizado menu principal com filtros (via ações globais)")

        except Exception as e:
            logger.error(f"Erro ao sincronizar menu principal com filtros: {e}", exc_info=True)

    def atualizar_contagem(self):
        try:
            main_loc = self.parent.loc if hasattr(self.parent, 'loc') else None

            if main_loc is None:
                from GerenciamentoUI.ui_12_Localizador import Localizador
                main_loc = Localizador()

            if self.parent and hasattr(self.parent, 'tabela_dados'):
                try:
                    total = self.parent.tabela_dados.rowCount()
                    visiveis = sum(1 for row in range(total) if not self.parent.tabela_dados.isRowHidden(row))

                    if total == 0:
                        return f"{main_loc.get_text('visible_filters')}: 0 / {main_loc.get_text('total_monitored')}: 0"

                    return f"{main_loc.get_text('visible_filters')}: {visiveis} / {main_loc.get_text('total_monitored')}: {total}"

                except RuntimeError:
                    logger.debug("Tabela de dados não está mais disponível")

            return f"{main_loc.get_text('visible_filters')}: 0 / {main_loc.get_text('total_monitored')}: 0"

        except Exception as e:
            logger.error(f"Erro ao atualizar contagem: {e}", exc_info=True)
            return "0 / 0"

    def verificar_filtro_operacao(self, tipo_operacao_traduzido):
        try:
            operacao_para_checkbox = {
                self.parent.loc.get_text("op_moved"): "op_moved",
                self.parent.loc.get_text("op_renamed"): "op_renamed",
                self.parent.loc.get_text("op_added"): "op_added",
                self.parent.loc.get_text("op_deleted"): "op_deleted",
                self.parent.loc.get_text("op_modified"): "op_modified",
                self.parent.loc.get_text("op_scanned"): "op_scanned"
            }

            checkbox_key = operacao_para_checkbox.get(tipo_operacao_traduzido)
            resultado = not checkbox_key or self.parent.checkboxes_operacao[checkbox_key].isChecked()
            return resultado

        except Exception as e:
            logger.error(f"Erro ao verificar filtro de operação '{tipo_operacao_traduzido}': {e}", exc_info=True)
            return True

    def atualizar_contagem_apos_idioma(self, idioma=None):
        try:
            from PySide6.QtCore import QTimer
            logger.debug(f"Agendando atualização após mudança de idioma para: {idioma}")

            self.parent.filtroAplicado.emit()
            QTimer.singleShot(100, self.notificar_alteracao_idioma)

        except Exception as e:
            logger.warning(f"Erro ao agendar atualização após mudança de idioma: {e}", exc_info=True)

    def notificar_alteracao_idioma(self):
        try:
            from PySide6.QtWidgets import QApplication
            logger.debug("Notificando componentes sobre alteração de idioma")

            for widget in QApplication.topLevelWidgets():
                if hasattr(widget, 'atualizar_status'):
                    widget.atualizar_status()

                if hasattr(widget, 'atualizar_interface'):
                    widget.atualizar_interface()

                if hasattr(widget, 'gerenciador_eventos_ui'):
                    try:
                        widget.gerenciador_eventos_ui.atualizar_interface()

                    except Exception as e:
                        logger.warning(f"Erro ao atualizar interface do gerenciador de eventos: {e}")

        except Exception as e:
            logger.warning(f"Erro ao notificar alteração de idioma: {e}", exc_info=True)

    def salvar_estado_checkboxes(self):
        try:
            if hasattr(self.parent, 'ignorar_mover'):
                AdministradorFiltros.filtros_estado["ignorar_mover"] = self.parent.ignorar_mover.isChecked()

            if hasattr(self.parent, 'ignorar_renomeados'):
                AdministradorFiltros.filtros_estado["ignorar_renomeados"] = self.parent.ignorar_renomeados.isChecked()

            if hasattr(self.parent, 'ignorar_adicionados'):
                AdministradorFiltros.filtros_estado["ignorar_adicionados"] = self.parent.ignorar_adicionados.isChecked()

            if hasattr(self.parent, 'ignorar_excluidos'):
                AdministradorFiltros.filtros_estado["ignorar_excluidos"] = self.parent.ignorar_excluidos.isChecked()

            if hasattr(self.parent, 'ignorar_data_modificados'):
                AdministradorFiltros.filtros_estado["ignorar_data_modificados"] = self.parent.ignorar_data_modificados.isChecked()

            if hasattr(self.parent, 'ignorar_escaneados'):
                AdministradorFiltros.filtros_estado["ignorar_escaneados"] = self.parent.ignorar_escaneados.isChecked()

            logger.debug(f"Estado dos filtros salvos: {AdministradorFiltros.filtros_estado}")

        except Exception as e:
            logger.error(f"Erro ao salvar estado dos filtros: {e}", exc_info=True)
