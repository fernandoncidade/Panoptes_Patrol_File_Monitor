import os
from utils.LogManager import LogManager
from datetime import datetime
from PySide6.QtWidgets import QFileDialog, QMessageBox

logger = LogManager.get_logger()


class GerenciadorDados:
    def __init__(self, interface_principal):
        self.interface = interface_principal

    def salvar_dados(self):
        logger.info("Salvando dados")

        if self.interface.ultimo_salvamento:
            logger.debug(f"Usando salvamento anterior: {self.interface.ultimo_salvamento['path']} (formato: {self.interface.ultimo_salvamento['format']})")
            self.interface.gerenciador_botoes.exportar_dados(
                self.interface.tabela_dados, 
                self.interface.ultimo_salvamento["format"], 
                self.interface.ultimo_salvamento["path"]
            )

        else:
            logger.debug("Nenhum salvamento anterior, abrindo diálogo")
            self.abrir_salvar_como()

    def abrir_salvar_como(self):
        logger.info("Abrindo diálogo 'Salvar Como'")
        dialog = QFileDialog(self.interface)
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setAcceptMode(QFileDialog.AcceptSave)

        filters = [
            "Excel Files (*.xlsx)",
            "CSV Files (*.csv)",
            "Text Files (*.txt)",
            "JSON Files (*.json)",
            "XML Files (*.xml)",
            "Database Files (*.db)"
        ]
        dialog.setNameFilters(filters)

        if dialog.exec():
            selected_file = dialog.selectedFiles()[0]
            file_format = dialog.selectedNameFilter()

            format_map = {
                "Excel Files (*.xlsx)": "xlsx",
                "CSV Files (*.csv)": "csv", 
                "Text Files (*.txt)": "txt",
                "JSON Files (*.json)": "json",
                "XML Files (*.xml)": "xml",
                "Database Files (*.db)": "db"
            }

            selected_format = format_map[file_format]

            expected_ext = f".{selected_format}"
            if not selected_file.lower().endswith(expected_ext):
                selected_file += expected_ext
                logger.debug(f"Adicionando extensão: {selected_file}")

            dest_dir = os.path.dirname(selected_file)
            if not os.path.exists(dest_dir):
                try:
                    os.makedirs(dest_dir, exist_ok=True)
                    logger.debug(f"Criado diretório: {dest_dir}")

                except Exception as e:
                    logger.error(f"Erro ao criar diretório: {e}", exc_info=True)
                    QMessageBox.warning(self.interface, self.interface.loc.get_text("error"), 
                                       self.interface.loc.get_text("dir_create_error"))
                    return

            self.interface.ultimo_salvamento = {
                "path": selected_file, 
                "format": selected_format, 
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            try:
                logger.info(f"Exportando para {selected_format}: {selected_file}")
                resultado = self.interface.gerenciador_botoes.exportar_dados(
                    self.interface.tabela_dados, selected_format, selected_file
                )

                if resultado:
                    QMessageBox.information(self.interface, 
                                           self.interface.loc.get_text("success"), 
                                           self.interface.loc.get_text("file_saved").format(selected_file))
                    logger.info(f"Arquivo salvo com sucesso: {selected_file}")

                else:
                    logger.warning("Exportação retornou status de falha")
                    QMessageBox.warning(self.interface, 
                                       self.interface.loc.get_text("warning"), 
                                       self.interface.loc.get_text("save_incomplete"))

            except Exception as e:
                logger.error(f"Erro ao exportar dados: {e}", exc_info=True)
                QMessageBox.critical(self.interface, 
                                    self.interface.loc.get_text("error"), 
                                    self.interface.loc.get_text("save_error").format(str(e)))
