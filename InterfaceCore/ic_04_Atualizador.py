from utils.LogManager import LogManager
from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout


class Atualizador:
    @staticmethod
    def atualizar_interface(interface):
        logger = LogManager.get_logger()
        try:
            logger.debug("Atualizando interface")
            interface.setWindowTitle(interface.loc.get_text("window_title"))

            if interface.diretorio_atual:
                interface.rotulo_diretorio.setText(interface.loc.get_text("dir_selected").format(interface.diretorio_atual))

            else:
                interface.rotulo_diretorio.setText(interface.loc.get_text("no_dir"))

            if interface.observador and interface.observador.ativo:
                interface.rotulo_resultado.setText(interface.loc.get_text("monitoring_started"))

            elif interface.observador and not interface.observador.ativo:
                interface.rotulo_resultado.setText(interface.loc.get_text("monitoring_stopped"))

            else:
                interface.rotulo_resultado.setText(interface.loc.get_text("select_to_start"))

            interface.gerenciador_menus_ui.criar_menu_principal()

            if hasattr(interface, 'gerenciador_tabela'):
                interface.gerenciador_tabela.configurar_tabela(interface.tabela_dados)

            if hasattr(interface, 'painel_filtros'):
                interface.painel_filtros.atualizar_interface()

            interface.gerenciador_botoes_ui.update_buttons_text(interface.loc)

            interface.atualizar_status()
            interface.update()
            QApplication.processEvents()
            logger.debug("Interface atualizada com sucesso")

        except Exception as e:
            logger.error(f"Erro ao atualizar interface: {e}", exc_info=True)

    @staticmethod
    def atualizar_status(interface, *args):
        logger = LogManager.get_logger()
        try:
            logger.debug("Atualizando status")
            if hasattr(interface, "label_contagem") and hasattr(interface, "painel_filtros"):
                interface.label_contagem.setText(interface.painel_filtros.atualizar_contagem())
                logger.debug("Status atualizado com sucesso")

        except Exception as e:
            logger.error(f"Erro ao atualizar status: {e}", exc_info=True)

    @staticmethod
    def abrir_janela_filtros(interface):
        logger = LogManager.get_logger()
        try:
            logger.debug("Abrindo janela de filtros")
            janela_filtros = QDialog(interface)
            janela_filtros.setWindowTitle(interface.loc.get_text("filters"))
            layout = QVBoxLayout(janela_filtros)

            from Filtros.fil_01_Filtros import Filtros
            painel_filtros = Filtros(interface.tabela_dados)
            painel_filtros.filtroAplicado.connect(interface.atualizar_status)

            layout.addWidget(painel_filtros)
            janela_filtros.setLayout(layout)
            janela_filtros.exec()
            logger.debug("Janela de filtros exibida")

        except Exception as e:
            logger.error(f"Erro ao abrir janela de filtros: {e}", exc_info=True)
