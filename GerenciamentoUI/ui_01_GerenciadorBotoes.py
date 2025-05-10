import json
import sqlite3
import xml.etree.ElementTree as ET
import pandas as pd
from PySide6.QtGui import Qt
from PySide6.QtCore import QMetaObject
from PySide6.QtWidgets import QFileDialog, QMessageBox
from Observador.ob_01_Observador import Observador


class GerenciadorBotoes:
    def __init__(self, interface, loc):
        self.interface = interface
        self.loc = loc

    def selecionar_diretorio(self):
        dir_selecionado = QFileDialog.getExistingDirectory(self.interface, self.loc.get_text("select_dir"))
        if dir_selecionado:
            self.interface.diretorio_atual = dir_selecionado
            self.interface.rotulo_diretorio.setText(self.loc.get_text("dir_selected").format(self.interface.diretorio_atual))

            if hasattr(self.interface, 'reiniciar_sistema_monitoramento'):
                self.interface.reiniciar_sistema_monitoramento()

            if not self.interface.observador:
                self.interface.observador = Observador(self.interface.diretorio_atual, self.interface.adicionar_evento)
                self.interface.observador.interface = self.interface

            else:
                self.interface.observador.diretorio = self.interface.diretorio_atual

    def alternar_analise_diretorio(self):
        try:
            if not self.interface.diretorio_atual:
                QMessageBox.warning(self.interface, self.loc.get_text("warning"), self.loc.get_text("select_first"))
                return

            if not self.interface.observador:
                self.interface.observador = Observador(self.interface.diretorio_atual, self.interface.adicionar_evento)
                self.interface.observador.interface = self.interface

            if not self.interface.observador.ativo:
                self.interface.observador.iniciar()
                self.interface.rotulo_resultado.setText(self.loc.get_text("monitoring_started"))

            else:
                self.interface.observador.parar()
                self.interface.rotulo_resultado.setText(self.loc.get_text("monitoring_stopped"))

        except Exception as e:
            print(f"Erro ao alternar análise: {e}")

    def exportar_dados(self, tabela_dados, formato, nome_arquivo=None):
        if tabela_dados.rowCount() == 0:
            QMessageBox.warning(None, self.loc.get_text("warning"), self.loc.get_text("no_data"))
            return False

        dados = []
        for row in range(tabela_dados.rowCount()):
            linha = {}
            for col in range(tabela_dados.columnCount()):
                header = tabela_dados.horizontalHeaderItem(col).text()
                item = tabela_dados.item(row, col)
                linha[header] = item.text() if item else ""

            dados.append(linha)

        df = pd.DataFrame(dados)

        try:
            if not nome_arquivo:
                if formato in ['xlsx', 'csv', 'txt']:
                    nome_arquivo, _ = QFileDialog.getSaveFileName(None, f"Exportar para {formato.upper()}", "", f"{formato.upper()} Files (*.{formato})")

                elif formato == 'json':
                    nome_arquivo, _ = QFileDialog.getSaveFileName(None, "Exportar para JSON", "", "JSON Files (*.json)")

                elif formato == 'xml':
                    nome_arquivo, _ = QFileDialog.getSaveFileName(None, "Exportar para XML", "", "XML Files (*.xml)")

                elif formato == 'db':
                    nome_arquivo, _ = QFileDialog.getSaveFileName(None, "Exportar para SQLite", "", "DB Files (*.db)")

            if nome_arquivo:
                try:
                    if formato == 'xlsx':
                        import os
                        import tempfile
                        import openpyxl

                        temp_dir = tempfile.gettempdir()
                        temp_file = os.path.join(temp_dir, "temp_export.xlsx")

                        df.to_excel(temp_file, index=False)

                        import shutil

                        shutil.copy2(temp_file, nome_arquivo)
                        os.remove(temp_file)

                    elif formato == 'csv':
                        df.to_csv(nome_arquivo, index=False)

                    elif formato == 'txt':
                        df.to_csv(nome_arquivo, index=False, sep='\t')

                    elif formato == 'json':
                        with open(nome_arquivo, 'w', encoding='utf-8') as f:
                            json.dump(dados, f, ensure_ascii=False, indent=4)

                    elif formato == 'xml':
                        root = ET.Element("eventos")
                        for evento in dados:
                            evento_element = ET.SubElement(root, "evento")
                            for key, value in evento.items():
                                child = ET.SubElement(evento_element, key.lower().replace(" ", "_"))
                                child.text = str(value)

                        tree = ET.ElementTree(root)
                        tree.write(nome_arquivo, encoding='utf-8', xml_declaration=True)

                    elif formato == 'db':
                        self._exportar_para_sqlite(dados, nome_arquivo)

                    return True

                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    QMessageBox.critical(None, self.loc.get_text("export_error"), 
                        self.loc.get_text("export_error_details").format(formato, str(e), error_details))

                    return False

            return False

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            QMessageBox.critical(None, self.loc.get_text("error"), 
                self.loc.get_text("export_preparation_error").format(str(e), error_details))

            return False

    def _exportar_para_sqlite(self, dados, nome_arquivo):
        try:
            conn = sqlite3.connect(nome_arquivo)
            cursor = conn.cursor()

            if dados:
                cursor.execute("DROP TABLE IF EXISTS eventos")
                colunas = list(dados[0].keys())
                create_query = f"CREATE TABLE eventos ({', '.join([f'{col.lower().replace(' ', '_')} TEXT' for col in colunas])})"
                cursor.execute(create_query)

                for evento in dados:
                    placeholders = ','.join(['?' for _ in evento])
                    insert_query = f"INSERT INTO eventos ({','.join([col.lower().replace(' ', '_') for col in evento.keys()])}) VALUES ({placeholders})"
                    cursor.execute(insert_query, list(evento.values()))

                conn.commit()

            conn.close()

        except sqlite3.Error as e:
            raise Exception(f"Erro ao exportar para SQLite: {str(e)}")

    def limpar_dados(self):
        try:
            if self.interface.observador:
                self.interface.observador.limpar_estado()

            self.interface.excluidos_recentemente.clear()
            self.interface.gerenciador_colunas.cache_metadados.clear()
            QMetaObject.invokeMethod(self.interface, "atualizar_status", Qt.QueuedConnection)

        except Exception as e:
            print(f"Erro ao limpar dados no gerenciador: {e}")
