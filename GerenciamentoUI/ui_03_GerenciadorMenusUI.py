from utils.LogManager import LogManager
import os
import sys
import json
from PySide6.QtGui import QAction, QActionGroup, QColor, QIcon, QPixmap, QPainter
from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QLabel, QPushButton, QTextBrowser, QSizePolicy, QHBoxLayout, QMenu
from PySide6.QtCore import Qt
from GerenciamentoUI.ui_11_DialogoCores import DialogoPaletaCores
from GerenciamentoUI.Localizacoes.tr_08_OpcoesSobre import (
    LICENSE_TEXT_PT_BR, LICENSE_TEXT_EN_US, LICENSE_TEXT_ES_ES, 
    LICENSE_TEXT_FR_FR, LICENSE_TEXT_IT_IT, LICENSE_TEXT_DE_DE, 
    SITE_LICENSES, NOTICE_TEXT_PT_BR, NOTICE_TEXT_EN_US, 
    NOTICE_TEXT_ES_ES, NOTICE_TEXT_FR_FR, NOTICE_TEXT_IT_IT, 
    NOTICE_TEXT_DE_DE, ABOUT_TEXT_PT_BR, ABOUT_TEXT_EN_US, 
    ABOUT_TEXT_ES_ES, ABOUT_TEXT_FR_FR, ABOUT_TEXT_IT_IT, 
    ABOUT_TEXT_DE_DE, Privacy_Policy_pt_BR, Privacy_Policy_en_US, 
    Privacy_Policy_es_ES, Privacy_Policy_fr_FR, Privacy_Policy_it_IT, 
    Privacy_Policy_de_DE
)

logger = LogManager.get_logger()


class MenuPersistente(QMenu):
    def __init__(self, titulo, parent=None):
        super().__init__(titulo, parent)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setMouseTracking(True)

    def mousePressEvent(self, event):
        action = self.actionAt(event.pos())
        if action and action.isEnabled():
            if not action.menu():
                action.trigger()
                event.accept()
                return

        super().mousePressEvent(event)

    def leaveEvent(self, event):
        pos = self.mapFromGlobal(self.parent().cursor().pos())
        if not self.rect().contains(pos):
            self.close()

        super().leaveEvent(event)

    def mouseReleaseEvent(self, event):
        action = self.actionAt(event.pos())
        if action and action.isEnabled() and not action.menu():
            event.accept()
            return

        super().mouseReleaseEvent(event)


class GerenciadorCores:
    def __init__(self, interface_principal):
        self.interface = interface_principal
        self.loc = interface_principal.loc

        self.cores_operacoes = {
            "op_renamed": "#00ff00",    # Verde
            "op_added": "#0000ff",      # Azul
            "op_deleted": "#ff0000",    # Vermelho
            "op_modified": "#ff6200",   # Laranja
            "op_moved": "#ff00ff",       # Roxo
            "op_scanned": "#808080"      # Cinza
        }

        self.carregar_cores()

    def carregar_cores(self):
        try:
            config_dir = self._obter_diretorio_config()
            cores_path = os.path.join(config_dir, "cores_config.json")

            if os.path.exists(cores_path):
                with open(cores_path, 'r', encoding='utf-8') as f:
                    cores_salvas = json.load(f)

                for tipo, cor in cores_salvas.get('cores_operacoes', {}).items():
                    if tipo in self.cores_operacoes:
                        self.cores_operacoes[tipo] = cor

                logger.info("Configurações de cores carregadas com sucesso")

            else:
                logger.info("Arquivo de configuração de cores não encontrado, usando valores padrão")

        except Exception as e:
            logger.error(f"Erro ao carregar configurações de cores: {e}", exc_info=True)

    def salvar_cores(self):
        try:
            config_dir = self._obter_diretorio_config()
            cores_path = os.path.join(config_dir, "cores_config.json")

            os.makedirs(config_dir, exist_ok=True)

            cores_config = {'cores_operacoes': self.cores_operacoes}

            with open(cores_path, 'w', encoding='utf-8') as f:
                json.dump(cores_config, f, indent=4)

            logger.info("Configurações de cores salvas com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar configurações de cores: {e}", exc_info=True)
            return False

    def _obter_diretorio_config(self):
        try:
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)

            else:
                base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            config_dir = os.path.join(base_path, "config")
            return config_dir

        except Exception:
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def obter_cor_qcolor(self, tipo_operacao):
        cor_hex = self.cores_operacoes.get(tipo_operacao, "#333333")
        return QColor(cor_hex)

    def obter_cor_hex(self, tipo_operacao):
        return self.cores_operacoes.get(tipo_operacao, "#333333")

    def definir_cor(self, tipo_operacao, cor_hex):
        if tipo_operacao in self.cores_operacoes:
            self.cores_operacoes[tipo_operacao] = cor_hex
            return True

        return False

    def atualizar_cores_no_sistema(self):
        if hasattr(self.interface, 'gerenciador_tabela'):
            self.interface.gerenciador_tabela.atualizacao_pendente = True
            self.interface.gerenciador_tabela.atualizar_dados_tabela(self.interface.tabela_dados)

        if hasattr(self.interface, 'gerenciador_estatisticas_ui') and hasattr(self.interface.gerenciador_estatisticas_ui, 'gerador_atual'):
            if self.interface.gerenciador_estatisticas_ui.gerador_atual:
                self.interface.gerenciador_estatisticas_ui.gerador_atual.atualizar_textos_traduzidos()

        self.interface.update()


class GerenciadorMenusUI:
    def __init__(self, interface_principal):
        self.interface = interface_principal
        self.loc = interface_principal.loc
        self.acoes_colunas = {}

        self.gerenciador_cores = GerenciadorCores(interface_principal)

    def criar_menu_principal(self):
        menu_bar = self.interface.menuBar()
        menu_bar.clear()

        menu_arquivo = MenuPersistente(self.loc.get_text("file_menu"), self.interface)
        menu_configuracoes = MenuPersistente(self.loc.get_text("settings"), self.interface)
        menu_opcoes = MenuPersistente(self.loc.get_text("options_menu"), self.interface)

        menu_bar.addMenu(menu_arquivo)
        menu_bar.addMenu(menu_configuracoes)
        menu_bar.addMenu(menu_opcoes)

        self._configurar_menu_arquivo(menu_arquivo)
        self._configurar_menu_configuracoes(menu_configuracoes)
        self._configurar_menu_opcoes(menu_opcoes)

    def _configurar_menu_arquivo(self, menu_arquivo):
        acoes = [
            {"texto": "select_dir", "slot": self.interface.selecionar_diretorio},
            {"texto": "start_stop", "slot": self.interface.alternar_analise_diretorio},
            {"texto": "save_as", "slot": self.interface.abrir_salvar_como},
            {"texto": "save", "slot": self.interface.salvar_dados},
            {"texto": "statistics", "slot": self.interface.mostrar_estatisticas},
            {"texto": "clear_data", "slot": self.interface.limpar_dados},
            {"texto": "exit", "slot": self.interface.sair_aplicacao}
        ]

        for acao in acoes:
            item_menu = QAction(self.loc.get_text(acao["texto"]), self.interface)
            item_menu.triggered.connect(acao["slot"])
            menu_arquivo.addAction(item_menu)

    def _configurar_menu_configuracoes(self, menu_configuracoes):
        submenu_filtros = MenuPersistente(self.loc.get_text("filters"), self.interface)
        menu_configuracoes.addMenu(submenu_filtros)
        grupo_filtros = QActionGroup(self.interface)
        grupo_filtros.setExclusive(False)

        for op in ["op_moved", "op_renamed", "op_added", "op_deleted", "op_modified", "op_scanned"]:
            acao_filtro = QAction(self.loc.get_text(op), self.interface)
            acao_filtro.setCheckable(True)
            acao_filtro.setChecked(True)
            acao_filtro.setData(op)
            acao_filtro.triggered.connect(self.interface.alternar_filtro)
            grupo_filtros.addAction(acao_filtro)
            submenu_filtros.addAction(acao_filtro)

        submenu_filtros.addSeparator()
        acao_filtros_avancados = QAction(self.loc.get_text("advanced_filters"), self.interface)
        acao_filtros_avancados.triggered.connect(self.interface.abrir_janela_filtros)
        submenu_filtros.addAction(acao_filtros_avancados)

        self._criar_submenu_colunas(menu_configuracoes)
        self._criar_submenu_cores(menu_configuracoes)
        self._criar_submenu_exportacao(menu_configuracoes)

    def _configurar_menu_opcoes(self, menu_opcoes):
        self._criar_submenu_idiomas(menu_opcoes)

        menu_opcoes.addSeparator()
        acao_sobre = QAction(self.loc.get_text("about"), self.interface)
        acao_sobre.triggered.connect(self._exibir_sobre)
        menu_opcoes.addAction(acao_sobre)

    def _criar_submenu_cores(self, menu_configuracoes):
        submenu_cores = MenuPersistente(self.loc.get_text("configure_colors") 
                                       if "configure_colors" in self.loc.traducoes.get(self.loc.idioma_atual, {}) 
                                       else "Configurar Cores", self.interface)
        menu_configuracoes.addMenu(submenu_cores)

        submenu_cores_operacoes = MenuPersistente(self.loc.get_text("operation_colors") 
                                                if "operation_colors" in self.loc.traducoes.get(self.loc.idioma_atual, {}) 
                                                else "Cores de Operações", self.interface)
        submenu_cores.addMenu(submenu_cores_operacoes)

        tipos_operacoes = {
            "op_renamed": self.loc.get_text("op_renamed"),
            "op_added": self.loc.get_text("op_added"),
            "op_deleted": self.loc.get_text("op_deleted"),
            "op_modified": self.loc.get_text("op_modified"),
            "op_moved": self.loc.get_text("op_moved"),
            "op_scanned": self.loc.get_text("op_scanned")
        }

        for op_key, op_text in tipos_operacoes.items():
            acao_cor = QAction(op_text, self.interface)
            acao_cor.setData(op_key)

            cor_atual = self.gerenciador_cores.obter_cor_hex(op_key)
            icone = self._criar_icone_cor(cor_atual)
            acao_cor.setIcon(icone)

            acao_cor.triggered.connect(lambda checked, op=op_key: self._abrir_dialogo_cor(op))
            submenu_cores_operacoes.addAction(acao_cor)

        submenu_cores.addSeparator()

        acao_resetar_cores = QAction(self.loc.get_text("reset_colors") 
                                     if "reset_colors" in self.loc.traducoes.get(self.loc.idioma_atual, {}) 
                                     else "Restaurar Cores Padrão", self.interface)

        acao_resetar_cores.triggered.connect(self._resetar_cores)
        submenu_cores.addAction(acao_resetar_cores)

    def _criar_icone_cor(self, cor_hex):
        tamanho = 16
        pixmap = QPixmap(tamanho, tamanho)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(cor_hex))
        painter.drawRect(0, 0, tamanho, tamanho)
        painter.end()

        return QIcon(pixmap)

    def _abrir_dialogo_cor(self, tipo_operacao):
        try:
            cor_atual = QColor(self.gerenciador_cores.obter_cor_hex(tipo_operacao))

            nome_operacao = self.loc.get_text(tipo_operacao)

            titulo = self.loc.get_text("select_color_for") if "select_color_for" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Selecionar Cor para"
            titulo = f"{titulo} {nome_operacao}"

            dialogo = DialogoPaletaCores(cor_atual, self.interface, titulo)
            if dialogo.exec() == QDialog.Accepted:
                nova_cor = dialogo.obter_cor()
                if nova_cor.isValid():
                    self.gerenciador_cores.definir_cor(tipo_operacao, nova_cor.name())
                    self.gerenciador_cores.salvar_cores()
                    self.gerenciador_cores.atualizar_cores_no_sistema()

                    exportar_colunas_ativas = self.acao_exportar_colunas_ativas.isChecked()
                    exportar_filtros_ativos = self.acao_exportar_filtros_ativos.isChecked()
                    exportar_selecao = self.acao_exportar_selecao.isChecked()

                    self.criar_menu_principal()

                    self.acao_exportar_colunas_ativas.setChecked(exportar_colunas_ativas)
                    self.acao_exportar_filtros_ativos.setChecked(exportar_filtros_ativos)
                    self.acao_exportar_selecao.setChecked(exportar_selecao)

                    mensagem = self.loc.get_text("color_changed_success") if "color_changed_success" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Cor alterada com sucesso!"
                    QMessageBox.information(self.interface, self.loc.get_text("success"), mensagem)

                    logger.info(f"Cor de {tipo_operacao} alterada para {nova_cor.name()}")

        except Exception as e:
            logger.error(f"Erro ao abrir diálogo de cor: {e}", exc_info=True)
            QMessageBox.critical(self.interface, self.loc.get_text("error"), f"{self.loc.get_text('error')}: {str(e)}")

    def _resetar_cores(self):
        try:
            cores_padrao = {
                "op_renamed": "#00ff00",    # Verde
                "op_added": "#0000ff",      # Azul
                "op_deleted": "#ff0000",    # Vermelho
                "op_modified": "#ff6200",   # Laranja
                "op_moved": "#ff00ff",       # Roxo
                "op_scanned": "#808080"      # Cinza
            }

            mensagem = self.loc.get_text("reset_colors_confirm") if "reset_colors_confirm" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Deseja restaurar todas as cores para os valores padrão?"
            resposta = QMessageBox.question(self.interface, self.loc.get_text("confirm"), mensagem, QMessageBox.Yes | QMessageBox.No)

            if resposta == QMessageBox.Yes:
                exportar_colunas_ativas = self.acao_exportar_colunas_ativas.isChecked()
                exportar_filtros_ativos = self.acao_exportar_filtros_ativos.isChecked()
                exportar_selecao = self.acao_exportar_selecao.isChecked()

                for tipo, cor in cores_padrao.items():
                    self.gerenciador_cores.definir_cor(tipo, cor)

                self.gerenciador_cores.salvar_cores()
                self.gerenciador_cores.atualizar_cores_no_sistema()

                self.criar_menu_principal()

                self.acao_exportar_colunas_ativas.setChecked(exportar_colunas_ativas)
                self.acao_exportar_filtros_ativos.setChecked(exportar_filtros_ativos)
                self.acao_exportar_selecao.setChecked(exportar_selecao)

                mensagem_sucesso = self.loc.get_text("colors_reset_success") if "colors_reset_success" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Cores restauradas com sucesso!"
                QMessageBox.information(self.interface, self.loc.get_text("success"), mensagem_sucesso)

                logger.info("Cores restauradas para valores padrão")

        except Exception as e:
            logger.error(f"Erro ao restaurar cores padrão: {e}", exc_info=True)
            QMessageBox.critical(self.interface, self.loc.get_text("error"), f"{self.loc.get_text('error')}: {str(e)}")

    def _criar_submenu_colunas(self, menu_configuracoes):
        submenu_colunas = MenuPersistente(self.loc.get_text("configure_columns"), self.interface)
        menu_configuracoes.addMenu(submenu_colunas)
        grupo_colunas = QActionGroup(self.interface)
        grupo_colunas.setExclusive(False)

        self.acoes_colunas.clear()

        for key, coluna in sorted(self.interface.gerenciador_colunas.COLUNAS_DISPONIVEIS.items(), key=lambda x: x[1]["ordem"]):
            acao_coluna = QAction(coluna["nome"], self.interface)
            acao_coluna.setCheckable(True)
            acao_coluna.setChecked(coluna["visivel"])
            acao_coluna.setData(key)
            acao_coluna.triggered.connect(self.interface.alternar_visibilidade_coluna)
            grupo_colunas.addAction(acao_coluna)
            submenu_colunas.addAction(acao_coluna)

            self.acoes_colunas[key] = acao_coluna

        submenu_colunas.addSeparator()

        acao_selecionar_todas = QAction(self.loc.get_text("select_all_columns") 
                                        if "select_all_columns" in self.loc.traducoes.get(self.loc.idioma_atual, {}) 
                                        else "Selecionar todas", self.interface)

        acao_selecionar_todas.triggered.connect(self.selecionar_todas_colunas)
        submenu_colunas.addAction(acao_selecionar_todas)

        acao_resetar_colunas = QAction(self.loc.get_text("reset_columns"), self.interface)
        acao_resetar_colunas.triggered.connect(self.interface.resetar_colunas)
        submenu_colunas.addAction(acao_resetar_colunas)

    def selecionar_todas_colunas(self):
        try:
            for key, acao in self.acoes_colunas.items():
                acao.setChecked(True)

            for key in self.acoes_colunas.keys():
                self.interface.gerenciador_colunas.COLUNAS_DISPONIVEIS[key]["visivel"] = True

            self.interface.atualizar_visibilidade_colunas()

            self.interface.gerenciador_colunas.salvar_configuracoes()

            logger.info("Todas as colunas foram selecionadas")

            msg_box = QMessageBox(self.interface)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(self.loc.get_text("success"))
            msg_box.setText(self.loc.get_text("columns_reset_success"))
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()

        except Exception as e:
            logger.error(f"Erro ao selecionar todas as colunas: {e}", exc_info=True)
            QMessageBox.critical(self.interface, self.loc.get_text("error"), f"{self.loc.get_text('error')}: {str(e)}")

    def _criar_submenu_exportacao(self, menu_configuracoes):
        submenu_exportacao = MenuPersistente(self.loc.get_text("export_options") 
                                            if "export_options" in self.loc.traducoes.get(self.loc.idioma_atual, {}) 
                                            else "Opções de Exportação", self.interface)
        menu_configuracoes.addMenu(submenu_exportacao)

        self.acao_exportar_colunas_ativas = QAction(self.loc.get_text("export_active_columns") 
                                                if "export_active_columns" in self.loc.traducoes.get(self.loc.idioma_atual, {}) 
                                                else "Exportar apenas colunas ativas", self.interface)
        self.acao_exportar_colunas_ativas.setCheckable(True)
        self.acao_exportar_colunas_ativas.setChecked(False)
        submenu_exportacao.addAction(self.acao_exportar_colunas_ativas)

        self.acao_exportar_filtros_ativos = QAction(self.loc.get_text("export_active_filters") 
                                                if "export_active_filters" in self.loc.traducoes.get(self.loc.idioma_atual, {}) 
                                                else "Exportar apenas filtros ativos", self.interface)
        self.acao_exportar_filtros_ativos.setCheckable(True)
        self.acao_exportar_filtros_ativos.setChecked(False)
        submenu_exportacao.addAction(self.acao_exportar_filtros_ativos)

        self.acao_exportar_selecao = QAction(self.loc.get_text("export_selected_data") 
                                            if "export_selected_data" in self.loc.traducoes.get(self.loc.idioma_atual, {}) 
                                            else "Exportar apenas dados selecionados", self.interface)
        self.acao_exportar_selecao.setCheckable(True)
        self.acao_exportar_selecao.setChecked(False)
        submenu_exportacao.addAction(self.acao_exportar_selecao)

        submenu_exportacao.addSeparator()

        acao_resetar_exportacao = QAction(self.loc.get_text("reset_export_options") 
                                        if "reset_export_options" in self.loc.traducoes.get(self.loc.idioma_atual, {}) 
                                        else "Restaurar Padrões", self.interface)
        acao_resetar_exportacao.triggered.connect(self._resetar_opcoes_exportacao)
        submenu_exportacao.addAction(acao_resetar_exportacao)

    def _resetar_opcoes_exportacao(self):
        try:
            self.acao_exportar_colunas_ativas.setChecked(False)
            self.acao_exportar_filtros_ativos.setChecked(False)
            self.acao_exportar_selecao.setChecked(False)

            mensagem_sucesso = self.loc.get_text("export_options_reset_success") if "export_options_reset_success" in self.loc.traducoes.get(self.loc.idioma_atual, {}) else "Opções de exportação restauradas para valores padrão!"
            QMessageBox.information(self.interface, self.loc.get_text("success"), mensagem_sucesso)

            logger.info("Opções de exportação restauradas para valores padrão")

        except Exception as e:
            logger.error(f"Erro ao restaurar opções de exportação: {e}", exc_info=True)
            QMessageBox.critical(self.interface, self.loc.get_text("error"), f"{self.loc.get_text('error')}: {str(e)}")

    def _criar_submenu_idiomas(self, menu_opcoes):
        submenu_idiomas = MenuPersistente(self.loc.get_text("language"), self.interface)
        menu_opcoes.addMenu(submenu_idiomas)
        grupo_idiomas = QActionGroup(self.interface)

        for codigo, nome in self.loc.get_idiomas_disponiveis().items():
            acao_idioma = QAction(nome, self.interface)
            acao_idioma.setCheckable(True)
            acao_idioma.setChecked(codigo == self.loc.idioma_atual)
            acao_idioma.setData(codigo)
            acao_idioma.triggered.connect(self.interface.alterar_idioma)
            grupo_idiomas.addAction(acao_idioma)
            submenu_idiomas.addAction(acao_idioma)

    def _exibir_sobre(self):
        try:
            textos_sobre = {
                "pt_BR": ABOUT_TEXT_PT_BR,
                "en_US": ABOUT_TEXT_EN_US,
                "es_ES": ABOUT_TEXT_ES_ES,
                "fr_FR": ABOUT_TEXT_FR_FR,
                "it_IT": ABOUT_TEXT_IT_IT,
                "de_DE": ABOUT_TEXT_DE_DE
            }

            textos_licenca = {
                "pt_BR": LICENSE_TEXT_PT_BR,
                "en_US": LICENSE_TEXT_EN_US,
                "es_ES": LICENSE_TEXT_ES_ES,
                "fr_FR": LICENSE_TEXT_FR_FR,
                "it_IT": LICENSE_TEXT_IT_IT,
                "de_DE": LICENSE_TEXT_DE_DE
            }

            textos_aviso = {
                "pt_BR": NOTICE_TEXT_PT_BR,
                "en_US": NOTICE_TEXT_EN_US,
                "es_ES": NOTICE_TEXT_ES_ES,
                "fr_FR": NOTICE_TEXT_FR_FR,
                "it_IT": NOTICE_TEXT_IT_IT,
                "de_DE": NOTICE_TEXT_DE_DE
            }

            textos_privacidade = {
                "pt_BR": Privacy_Policy_pt_BR,
                "en_US": Privacy_Policy_en_US,
                "es_ES": Privacy_Policy_es_ES,
                "fr_FR": Privacy_Policy_fr_FR,
                "it_IT": Privacy_Policy_it_IT,
                "de_DE": Privacy_Policy_de_DE
            }

            texto_sobre = textos_sobre.get(self.loc.idioma_atual, textos_sobre["en_US"])
            texto_licenca = textos_licenca.get(self.loc.idioma_atual, textos_licenca["en_US"])
            texto_aviso = textos_aviso.get(self.loc.idioma_atual, textos_aviso["en_US"])
            texto_privacidade = textos_privacidade.get(self.loc.idioma_atual, textos_privacidade["en_US"])

            dialog = SobreDialog(
                self.interface,
                titulo=f"{self.loc.get_text('about')} - PANOPTES PATROL",
                cabecalho=(
                    "<h3>PANOPTES PATROL</h3>"
                    f"<p><b>{self.loc.get_text('version')}:</b> 0.1.0</p>"
                    f"<p><b>{self.loc.get_text('authors')}:</b> Fernando Nillsson Cidade</p>"
                    f"<p><b>{self.loc.get_text('description')}:</b> {self.loc.get_text('description_text')}</p>"
                ),
                detalhes=texto_sobre,
                licencas=texto_licenca,
                sites_licencas=SITE_LICENSES,
                show_details_text=self.loc.get_text("show_details"),
                hide_details_text=self.loc.get_text("hide_details"),
                show_licenses_text=self.loc.get_text("show_licenses"),
                hide_licenses_text=self.loc.get_text("hide_licenses"),
                ok_text=self.loc.get_text("ok"),
                site_oficial_text=self.loc.get_text("site_oficial"),
                avisos=texto_aviso,
                show_notices_text=self.loc.get_text("show_notices"),
                hide_notices_text=self.loc.get_text("hide_notices"),
                Privacy_Policy=texto_privacidade,
                show_privacy_policy_text=self.loc.get_text("show_privacy_policy"),
                hide_privacy_policy_text=self.loc.get_text("hide_privacy_policy"),
                info_not_available_text=self.loc.get_text("information_not_available")
            )

            tamanho_principal = self.interface.size()
            dialog.resize(int(tamanho_principal.width() * 0.8), int(tamanho_principal.height() * 0.7))

            dialog.exec()
            logger.info("Diálogo 'Sobre' exibido com sucesso")

        except Exception as e:
            logger.error(f"Erro ao exibir o diálogo 'Sobre': {e}", exc_info=True)
            QMessageBox.critical(self.interface, self.loc.get_text("error"), f"{self.loc.get_text('error')}: {str(e)}")


class SobreDialog(QDialog):
    def __init__(self, parent, titulo, cabecalho, detalhes, licencas, sites_licencas, show_details_text, hide_details_text, 
                 show_licenses_text, hide_licenses_text, ok_text, site_oficial_text, avisos=None, show_notices_text=None, 
                 hide_notices_text=None, Privacy_Policy=None, show_privacy_policy_text=None, hide_privacy_policy_text=None, 
                 info_not_available_text="Information not available"):
        super().__init__(parent)
        self.setWindowTitle(titulo)

        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)

        layout = QVBoxLayout(self)

        self.header_label = QLabel(cabecalho)
        self.header_label.setTextFormat(Qt.TextFormat.RichText)
        self.header_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.header_label)

        button_layout = QHBoxLayout()

        self.details_button = QPushButton(show_details_text)
        self.details_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.details_button.clicked.connect(self.toggle_details)
        button_layout.addWidget(self.details_button)

        self.licenses_button = QPushButton(show_licenses_text)
        self.licenses_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.licenses_button.clicked.connect(self.toggle_licenses)
        button_layout.addWidget(self.licenses_button)

        self.notices_button = QPushButton(show_notices_text)
        self.notices_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.notices_button.clicked.connect(self.toggle_notices)
        button_layout.addWidget(self.notices_button)

        self.privacy_policy_button = QPushButton(show_privacy_policy_text)
        self.privacy_policy_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.privacy_policy_button.clicked.connect(self.toggle_privacy_policy)
        button_layout.addWidget(self.privacy_policy_button)

        self.ok_button = QPushButton(ok_text)
        self.ok_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        button_layout.addStretch(1)

        layout.addLayout(button_layout)

        self.details_edit = QTextBrowser()
        self.details_edit.setReadOnly(True)
        self.details_edit.setVisible(False)
        self.details_edit.setOpenExternalLinks(True)
        layout.addWidget(self.details_edit, 1)

        self.show_details_text = show_details_text
        self.hide_details_text = hide_details_text
        self.show_licenses_text = show_licenses_text
        self.hide_licenses_text = hide_licenses_text
        self.show_notices_text = show_notices_text
        self.hide_notices_text = hide_notices_text
        self.show_privacy_policy_text = show_privacy_policy_text
        self.hide_privacy_policy_text = hide_privacy_policy_text
        self.site_oficial_text = site_oficial_text
        self.info_not_available_text = info_not_available_text

        self.detalhes = detalhes
        self.licencas = licencas
        self.sites_licencas = sites_licencas
        self.avisos = avisos
        self.Privacy_Policy = Privacy_Policy

        self.showing_details = False
        self.showing_licenses = False
        self.showing_notices = False
        self.showing_privacy_policy = False

        self.setMinimumSize(500, 300)

    def toggle_details(self):
        if self.showing_licenses:
            self.showing_licenses = False
            self.licenses_button.setText(self.show_licenses_text)

        if self.showing_notices:
            self.showing_notices = False
            self.notices_button.setText(self.show_notices_text)

        if hasattr(self, 'showing_privacy_policy') and self.showing_privacy_policy:
            self.showing_privacy_policy = False
            self.privacy_policy_button.setText(self.show_privacy_policy_text)

        self.showing_details = not self.showing_details
        self.details_edit.setVisible(self.showing_details)

        if self.showing_details:
            self.details_button.setText(self.hide_details_text)
            self.details_edit.setPlainText(self.detalhes)

        else:
            self.details_button.setText(self.show_details_text)

        self._adjust_dialog_size()

    def toggle_licenses(self):
        if self.showing_details:
            self.showing_details = False
            self.details_button.setText(self.show_details_text)

        if self.showing_notices:
            self.showing_notices = False
            self.notices_button.setText(self.show_notices_text)

        if hasattr(self, 'showing_privacy_policy') and self.showing_privacy_policy:
            self.showing_privacy_policy = False
            self.privacy_policy_button.setText(self.show_privacy_policy_text)

        self.showing_licenses = not self.showing_licenses
        self.details_edit.setVisible(self.showing_licenses)

        if self.showing_licenses:
            self.licenses_button.setText(self.hide_licenses_text)

            texto_html = self.licencas.replace('\n', '<br>')

            texto_html += f"<br><br><h3>{self.site_oficial_text}</h3><ul>"
            for site in self.sites_licencas.strip().split('\n'):
                if site.strip():
                    texto_html += f'<li><a href="{site.strip()}">{site.strip()}</a></li>'

            texto_html += "</ul>"

            self.details_edit.setHtml(texto_html)

        else:
            self.licenses_button.setText(self.show_licenses_text)
            self.details_edit.clear()

        self._adjust_dialog_size()

    def toggle_notices(self):
        if self.showing_details:
            self.showing_details = False
            self.details_button.setText(self.show_details_text)

        if self.showing_licenses:
            self.showing_licenses = False
            self.licenses_button.setText(self.show_licenses_text)

        if hasattr(self, 'showing_privacy_policy') and self.showing_privacy_policy:
            self.showing_privacy_policy = False
            self.privacy_policy_button.setText(self.show_privacy_policy_text)

        self.showing_notices = not self.showing_notices
        self.details_edit.setVisible(self.showing_notices)

        if self.showing_notices:
            self.notices_button.setText(self.hide_notices_text)

            if self.avisos:
                self.details_edit.setHtml(self.avisos.replace('\n', '<br>'))

            else:
                self.details_edit.setHtml(f"<p>{self.info_not_available_text}.</p>")

        else:
            self.notices_button.setText(self.show_notices_text)
            self.details_edit.clear()

        self._adjust_dialog_size()

    def toggle_privacy_policy(self):
        if self.showing_details:
            self.showing_details = False
            self.details_button.setText(self.show_details_text)

        if self.showing_licenses:
            self.showing_licenses = False
            self.licenses_button.setText(self.show_licenses_text)

        if self.showing_notices:
            self.showing_notices = False
            self.notices_button.setText(self.show_notices_text)

        self.showing_privacy_policy = not getattr(self, 'showing_privacy_policy', False)
        self.details_edit.setVisible(self.showing_privacy_policy)

        if self.showing_privacy_policy:
            self.privacy_policy_button.setText(self.hide_privacy_policy_text)

            if self.Privacy_Policy:
                self.details_edit.setHtml(self.Privacy_Policy.replace('\n', '<br>'))

            else:
                self.details_edit.setHtml(f"<p>{self.info_not_available_text}.</p>")

        else:
            self.privacy_policy_button.setText(self.show_privacy_policy_text)
            self.details_edit.clear()

        self._adjust_dialog_size()

    def _adjust_dialog_size(self):
        if self.showing_details or self.showing_licenses or self.showing_notices:
            current_size = self.size()
            if current_size.height() < 450:
                self.resize(current_size.width(), 450)
