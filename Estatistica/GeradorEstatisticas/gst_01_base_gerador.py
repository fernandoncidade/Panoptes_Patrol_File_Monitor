import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from utils.LogManager import LogManager

logger = LogManager.get_logger()


class BaseGerador:
    __slots__ = ['db_path', 'loc', 'interface', 'cores_operacoes', '__weakref__']

    def __init__(self, db_path, localizador=None, interface_principal=None):
        logger.debug(f"Inicializando BaseGerador com banco de dados: {db_path}")
        self.db_path = db_path
        self.loc = localizador
        self.interface = interface_principal
        self.cores_operacoes = {}

        import logging
        logging.getLogger('matplotlib').setLevel(logging.WARNING)
        logger.debug("Nível de log do matplotlib configurado para WARNING")

        self._configurar_estilo()
        self._atualizar_textos_traduzidos()

        if self.loc and hasattr(self.loc, 'idioma_alterado'):
            self.loc.idioma_alterado.connect(self._atualizar_textos_traduzidos)
            logger.debug("Sinal de idioma_alterado conectado ao método _atualizar_textos_traduzidos")

        else:
            logger.debug("Localizador não disponível ou não possui sinal idioma_alterado")

    def _configurar_estilo(self):
        try:
            logger.debug("Configurando estilo dos gráficos")
            plt.style.use('bmh')

            plt.rcParams.update({
                'axes.titlesize': 12,
                'axes.titleweight': 'bold',
                'figure.titlesize': 14,
                'figure.titleweight': 'bold',
                'lines.linewidth': 2,
                'lines.markersize': 8,
                'legend.fontsize': 10,
                'legend.framealpha': 0.8
            })

            plt.rcParams['figure.facecolor'] = 'white'
            plt.rcParams['axes.facecolor'] = 'white'
            plt.rcParams['axes.grid'] = True
            plt.rcParams['grid.alpha'] = 0.3
            plt.rcParams['axes.labelsize'] = 10
            plt.rcParams['xtick.labelsize'] = 9
            plt.rcParams['ytick.labelsize'] = 9
            plt.rcParams['font.family'] = 'sans-serif'
            logger.debug("Estilo dos gráficos configurado com sucesso")

        except Exception as e:
            logger.error(f"Erro ao configurar estilo dos gráficos: {e}", exc_info=True)

    def _atualizar_textos_traduzidos(self):
        logger.debug("Atualizando textos traduzidos e cores para operações")
        try:
            gerenciador_cores = None

            if self.interface and hasattr(self.interface, 'gerenciador_menus_ui') and hasattr(self.interface.gerenciador_menus_ui, 'gerenciador_cores'):
                gerenciador_cores = self.interface.gerenciador_menus_ui.gerenciador_cores
                logger.debug("Gerenciador de cores obtido da interface principal")

            if gerenciador_cores:
                self.cores_operacoes = {
                    self.loc.get_text("op_renamed") if self.loc else 'Renomeado': gerenciador_cores.obter_cor_hex("op_renamed"),
                    self.loc.get_text("op_added") if self.loc else 'Adicionado': gerenciador_cores.obter_cor_hex("op_added"),
                    self.loc.get_text("op_deleted") if self.loc else 'Excluído': gerenciador_cores.obter_cor_hex("op_deleted"),
                    self.loc.get_text("op_modified") if self.loc else 'Modificado': gerenciador_cores.obter_cor_hex("op_modified"),
                    self.loc.get_text("op_moved") if self.loc else 'Movido': gerenciador_cores.obter_cor_hex("op_moved"),
                    self.loc.get_text("op_scanned") if self.loc else 'Escaneado': gerenciador_cores.obter_cor_hex("op_scanned"),
                }
                logger.debug("Cores personalizadas aplicadas do gerenciador de cores")

            else:
                self.cores_operacoes = {
                    self.loc.get_text("op_renamed") if self.loc else 'Renomeado': '#00ff00',
                    self.loc.get_text("op_added") if self.loc else 'Adicionado': '#0000ff',
                    self.loc.get_text("op_deleted") if self.loc else 'Excluído': '#ff0000',
                    self.loc.get_text("op_modified") if self.loc else 'Modificado': '#ff6200',
                    self.loc.get_text("op_moved") if self.loc else 'Movido': '#ff00ff',
                    self.loc.get_text("op_scanned") if self.loc else 'Escaneado': '#808080',
                }
                logger.debug("Cores padrão aplicadas (gerenciador de cores não disponível)")

        except Exception as e:
            logger.error(f"Erro ao atualizar textos traduzidos: {e}", exc_info=True)

    def _obter_dados(self):
        logger.debug("Obtendo dados do banco de dados para geração de gráficos")

        try:
            query = """
                SELECT tipo_operacao, tipo, timestamp, tamanho 
                FROM monitoramento 
                WHERE timestamp IS NOT NULL
            """
            logger.debug(f"Executando query SQL: {query}")

            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn)

            num_registros = len(df)
            logger.debug(f"Dados obtidos com sucesso: {num_registros} registros")

            if self.loc:
                logger.debug("Traduzindo dados obtidos")
                df = self._traduzir_dados(df)

            return df

        except sqlite3.Error as e:
            logger.error(f"Erro SQL ao obter dados: {e}", exc_info=True)
            return pd.DataFrame()

        except Exception as e:
            logger.error(f"Erro ao obter dados: {e}", exc_info=True)
            return pd.DataFrame()

    def _traduzir_dados(self, df):
        logger.debug("Iniciando tradução de dados")

        try:
            mapeamento_operacoes = self._obter_mapeamento_operacoes()
            logger.debug(f"Mapeamento de operações contém {len(mapeamento_operacoes)} entradas")
            df['tipo_operacao'] = df['tipo_operacao'].map(lambda x: mapeamento_operacoes.get(x, x))

            # Tradução dos tipos de arquivo
            mapeamento_tipos = self._obter_mapeamento_tipos()
            logger.debug(f"Mapeamento de tipos contém {len(mapeamento_tipos)} entradas")
            df['tipo'] = df['tipo'].map(lambda x: mapeamento_tipos.get(x, x))

            logger.debug("Dados traduzidos com sucesso")
            return df

        except Exception as e:
            logger.error(f"Erro ao traduzir dados: {e}", exc_info=True)
            return df

    def _obter_mapeamento_operacoes(self):
        try:
            logger.debug("Obtendo mapeamento de operações para traduções")
            return {
                # Inglês
                "Added": self.loc.get_text("op_added"),
                "Deleted": self.loc.get_text("op_deleted"),
                "Modified": self.loc.get_text("op_modified"),
                "Renamed": self.loc.get_text("op_renamed"),
                "Moved": self.loc.get_text("op_moved"),
                "Scanned": self.loc.get_text("op_scanned"),
                # Português
                "Adicionado": self.loc.get_text("op_added"),
                "Excluído": self.loc.get_text("op_deleted"),
                "Modificado": self.loc.get_text("op_modified"),
                "Renomeado": self.loc.get_text("op_renamed"),
                "Movido": self.loc.get_text("op_moved"),
                "Escaneado": self.loc.get_text("op_scanned"),
                # Espanhol
                "Añadido": self.loc.get_text("op_added"),
                "Eliminado": self.loc.get_text("op_deleted"),
                "Modificado": self.loc.get_text("op_modified"),
                "Renombrado": self.loc.get_text("op_renamed"),
                "Movido": self.loc.get_text("op_moved"),
                "Escaneado": self.loc.get_text("op_scanned"),
                # Francês
                "Ajouté": self.loc.get_text("op_added"),
                "Supprimé": self.loc.get_text("op_deleted"),
                "Modifié": self.loc.get_text("op_modified"),
                "Renommé": self.loc.get_text("op_renamed"),
                "Déplacé": self.loc.get_text("op_moved"),
                "Numérisé": self.loc.get_text("op_scanned"),
                # Italiano
                "Aggiunto": self.loc.get_text("op_added"),
                "Eliminato": self.loc.get_text("op_deleted"),
                "Modificato": self.loc.get_text("op_modified"),
                "Rinominato": self.loc.get_text("op_renamed"),
                "Spostato": self.loc.get_text("op_moved"),
                "Scansionato": self.loc.get_text("op_scanned"),
                # Alemão
                "Hinzugefügt": self.loc.get_text("op_added"),
                "Gelöscht": self.loc.get_text("op_deleted"),
                "Geändert": self.loc.get_text("op_modified"),
                "Umbenannt": self.loc.get_text("op_renamed"),
                "Verschoben": self.loc.get_text("op_moved"),
                "Gescannt": self.loc.get_text("op_scanned")
            }

        except Exception as e:
            logger.error(f"Erro ao obter mapeamento de operações: {e}", exc_info=True)
            return {}

    def _obter_mapeamento_tipos(self):
        try:
            logger.debug("Obtendo mapeamento de tipos de arquivos para traduções")
            return {
                # Inglês
                "unknown": self.loc.get_text("unknown"),
                "Unknown": self.loc.get_text("unknown"),
                "folder": self.loc.get_text("folder"),
                "Folder": self.loc.get_text("folder"),
                "video": self.loc.get_text("file_video"),
                "Video": self.loc.get_text("file_video"),
                "image": self.loc.get_text("file_image"),
                "Image": self.loc.get_text("file_image"),
                "audio": self.loc.get_text("file_audio"),
                "Audio": self.loc.get_text("file_audio"),
                "source code": self.loc.get_text("file_source_code"),
                "Source code": self.loc.get_text("file_source_code"),
                "document": self.loc.get_text("file_document"),
                "Document": self.loc.get_text("file_document"),
                "spreadsheet": self.loc.get_text("file_spreadsheet"),
                "Spreadsheet": self.loc.get_text("file_spreadsheet"),
                "presentation": self.loc.get_text("file_presentation"),
                "Presentation": self.loc.get_text("file_presentation"),
                "database": self.loc.get_text("file_database"),
                "Database": self.loc.get_text("file_database"),
                "executable": self.loc.get_text("file_executable"),
                "Executable": self.loc.get_text("file_executable"),
                "temporary": self.loc.get_text("file_temp"),
                "Temporary": self.loc.get_text("file_temp"),
                "archive": self.loc.get_text("file_archive"),
                "Archive": self.loc.get_text("file_archive"),
                "backup": self.loc.get_text("file_backup"),
                "Backup": self.loc.get_text("file_backup"),
                "log": self.loc.get_text("file_log"),
                "Log": self.loc.get_text("file_log"),
                "config": self.loc.get_text("file_config"),
                "Config": self.loc.get_text("file_config"),
                # Português
                "pasta": self.loc.get_text("folder"),
                "Pasta": self.loc.get_text("folder"),
                "vídeo": self.loc.get_text("file_video"),
                "Vídeo": self.loc.get_text("file_video"),
                "imagem": self.loc.get_text("file_image"),
                "Imagem": self.loc.get_text("file_image"),
                "áudio": self.loc.get_text("file_audio"),
                "Áudio": self.loc.get_text("file_audio"),
                "audio": self.loc.get_text("file_audio"),
                "Audio": self.loc.get_text("file_audio"),
                "código fonte": self.loc.get_text("file_source_code"),
                "Código fonte": self.loc.get_text("file_source_code"),
                "documento": self.loc.get_text("file_document"),
                "Documento": self.loc.get_text("file_document"),
                "planilha": self.loc.get_text("file_spreadsheet"),
                "Planilha": self.loc.get_text("file_spreadsheet"),
                "apresentação": self.loc.get_text("file_presentation"),
                "Apresentação": self.loc.get_text("file_presentation"),
                "banco de dados": self.loc.get_text("file_database"),
                "Banco de dados": self.loc.get_text("file_database"),
                "executável": self.loc.get_text("file_executable"),
                "Executável": self.loc.get_text("file_executable"),
                "temporário": self.loc.get_text("file_temp"),
                "Temporário": self.loc.get_text("file_temp"),
                "compactado": self.loc.get_text("file_archive"),
                "Compactado": self.loc.get_text("file_archive"),
                "backup": self.loc.get_text("file_backup"),
                "Backup": self.loc.get_text("file_backup"),
                "log": self.loc.get_text("file_log"),
                "Log": self.loc.get_text("file_log"),
                "configuração": self.loc.get_text("file_config"),
                "Configuração": self.loc.get_text("file_config"),
                "desconhecido": self.loc.get_text("unknown"),
                "Desconhecido": self.loc.get_text("unknown"),
                # Espanhol
                "carpeta": self.loc.get_text("folder"),
                "Carpeta": self.loc.get_text("folder"),
                "video": self.loc.get_text("file_video"),
                "Video": self.loc.get_text("file_video"),
                "imagen": self.loc.get_text("file_image"),
                "Imagen": self.loc.get_text("file_image"),
                "audio": self.loc.get_text("file_audio"),
                "Audio": self.loc.get_text("file_audio"),
                "código fuente": self.loc.get_text("file_source_code"),
                "Código fuente": self.loc.get_text("file_source_code"),
                "documento": self.loc.get_text("file_document"),
                "Documento": self.loc.get_text("file_document"),
                "hoja de cálculo": self.loc.get_text("file_spreadsheet"),
                "Hoja de cálculo": self.loc.get_text("file_spreadsheet"),
                "presentación": self.loc.get_text("file_presentation"),
                "Presentación": self.loc.get_text("file_presentation"),
                "base de datos": self.loc.get_text("file_database"),
                "Base de datos": self.loc.get_text("file_database"),
                "ejecutable": self.loc.get_text("file_executable"),
                "Ejecutable": self.loc.get_text("file_executable"),
                "temporal": self.loc.get_text("file_temp"),
                "Temporal": self.loc.get_text("file_temp"),
                "archivo": self.loc.get_text("file_archive"),
                "Archivo": self.loc.get_text("file_archive"),
                "comprimido": self.loc.get_text("file_archive"),
                "Comprimido": self.loc.get_text("file_archive"),
                "respaldo": self.loc.get_text("file_backup"),
                "Respaldo": self.loc.get_text("file_backup"),
                "copia de seguridad": self.loc.get_text("file_backup"),
                "Copia de seguridad": self.loc.get_text("file_backup"),
                "registro": self.loc.get_text("file_log"),
                "Registro": self.loc.get_text("file_log"),
                "configuración": self.loc.get_text("file_config"),
                "Configuración": self.loc.get_text("file_config"),
                "desconocido": self.loc.get_text("unknown"),
                "Desconocido": self.loc.get_text("unknown"),
                # Francês
                "dossier": self.loc.get_text("folder"),
                "Dossier": self.loc.get_text("folder"),
                "vidéo": self.loc.get_text("file_video"),
                "Vidéo": self.loc.get_text("file_video"),
                "image": self.loc.get_text("file_image"),
                "Image": self.loc.get_text("file_image"),
                "audio": self.loc.get_text("file_audio"),
                "Audio": self.loc.get_text("file_audio"),
                "code source": self.loc.get_text("file_source_code"),
                "Code source": self.loc.get_text("file_source_code"),
                "document": self.loc.get_text("file_document"),
                "Document": self.loc.get_text("file_document"),
                "feuille de calcul": self.loc.get_text("file_spreadsheet"),
                "Feuille de calcul": self.loc.get_text("file_spreadsheet"),
                "tableur": self.loc.get_text("file_spreadsheet"),
                "Tableur": self.loc.get_text("file_spreadsheet"),
                "présentation": self.loc.get_text("file_presentation"),
                "Présentation": self.loc.get_text("file_presentation"),
                "base de données": self.loc.get_text("file_database"),
                "Base de données": self.loc.get_text("file_database"),
                "exécutable": self.loc.get_text("file_executable"),
                "Exécutable": self.loc.get_text("file_executable"),
                "temporaire": self.loc.get_text("file_temp"),
                "Temporaire": self.loc.get_text("file_temp"),
                "archive": self.loc.get_text("file_archive"),
                "Archive": self.loc.get_text("file_archive"),
                "compressé": self.loc.get_text("file_archive"),
                "Compressé": self.loc.get_text("file_archive"),
                "sauvegarde": self.loc.get_text("file_backup"),
                "Sauvegarde": self.loc.get_text("file_backup"),
                "journal": self.loc.get_text("file_log"),
                "Journal": self.loc.get_text("file_log"),
                "configuration": self.loc.get_text("file_config"),
                "Configuration": self.loc.get_text("file_config"),
                "inconnu": self.loc.get_text("unknown"),
                "Inconnu": self.loc.get_text("unknown"),
                # Italiano
                "cartella": self.loc.get_text("folder"),
                "Cartella": self.loc.get_text("folder"),
                "video": self.loc.get_text("file_video"),
                "Video": self.loc.get_text("file_video"),
                "immagine": self.loc.get_text("file_image"),
                "Immagine": self.loc.get_text("file_image"),
                "audio": self.loc.get_text("file_audio"),
                "Audio": self.loc.get_text("file_audio"),
                "codice sorgente": self.loc.get_text("file_source_code"),
                "Codice sorgente": self.loc.get_text("file_source_code"),
                "documento": self.loc.get_text("file_document"),
                "Documento": self.loc.get_text("file_document"),
                "foglio di calcolo": self.loc.get_text("file_spreadsheet"),
                "Foglio di calcolo": self.loc.get_text("file_spreadsheet"),
                "presentazione": self.loc.get_text("file_presentation"),
                "Presentazione": self.loc.get_text("file_presentation"),
                "database": self.loc.get_text("file_database"),
                "Database": self.loc.get_text("file_database"),
                "eseguibile": self.loc.get_text("file_executable"),
                "Eseguibile": self.loc.get_text("file_executable"),
                "temporaneo": self.loc.get_text("file_temp"),
                "Temporaneo": self.loc.get_text("file_temp"),
                "archivio": self.loc.get_text("file_archive"),
                "Archivio": self.loc.get_text("file_archive"),
                "compresso": self.loc.get_text("file_archive"),
                "Compresso": self.loc.get_text("file_archive"),
                "backup": self.loc.get_text("file_backup"),
                "Backup": self.loc.get_text("file_backup"),
                "registro": self.loc.get_text("file_log"),
                "Registro": self.loc.get_text("file_log"),
                "configurazione": self.loc.get_text("file_config"),
                "Configurazione": self.loc.get_text("file_config"),
                "sconosciuto": self.loc.get_text("unknown"),
                "Sconosciuto": self.loc.get_text("unknown"),
                # Alemão
                "ordner": self.loc.get_text("folder"),
                "Ordner": self.loc.get_text("folder"),
                "video": self.loc.get_text("file_video"),
                "Video": self.loc.get_text("file_video"),
                "bild": self.loc.get_text("file_image"),
                "Bild": self.loc.get_text("file_image"),
                "audio": self.loc.get_text("file_audio"),
                "Audio": self.loc.get_text("file_audio"),
                "quellcode": self.loc.get_text("file_source_code"),
                "Quellcode": self.loc.get_text("file_source_code"),
                "dokument": self.loc.get_text("file_document"),
                "Dokument": self.loc.get_text("file_document"),
                "tabellenkalkulation": self.loc.get_text("file_spreadsheet"),
                "Tabellenkalkulation": self.loc.get_text("file_spreadsheet"),
                "präsentation": self.loc.get_text("file_presentation"),
                "Präsentation": self.loc.get_text("file_presentation"),
                "datenbank": self.loc.get_text("file_database"),
                "Datenbank": self.loc.get_text("file_database"),
                "ausführbare datei": self.loc.get_text("file_executable"),
                "Ausführbare Datei": self.loc.get_text("file_executable"),
                "temporär": self.loc.get_text("file_temp"),
                "Temporär": self.loc.get_text("file_temp"),
                "archiv": self.loc.get_text("file_archive"),
                "Archiv": self.loc.get_text("file_archive"),
                "komprimiert": self.loc.get_text("file_archive"),
                "Komprimiert": self.loc.get_text("file_archive"),
                "sicherung": self.loc.get_text("file_backup"),
                "Sicherung": self.loc.get_text("file_backup"),
                "backup": self.loc.get_text("file_backup"),
                "Backup": self.loc.get_text("file_backup"),
                "protokoll": self.loc.get_text("file_log"),
                "Protokoll": self.loc.get_text("file_log"),
                "konfiguration": self.loc.get_text("file_config"),
                "Konfiguration": self.loc.get_text("file_config"),
                "unbekannt": self.loc.get_text("unknown"),
                "Unbekannt": self.loc.get_text("unknown")
            }

        except Exception as e:
            logger.error(f"Erro ao obter mapeamento de tipos: {e}", exc_info=True)
            return {}

    def _criar_grafico_sem_dados(self, titulo):
        logger.warning(f"Criando gráfico sem dados para '{titulo}'")
        try:
            plt.figure(figsize=(12, 6))
            plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados para exibir', 
                    horizontalalignment='center',
                    verticalalignment='center')

            plt.title(titulo)
            plt.axis('off')
            logger.debug("Gráfico sem dados criado com sucesso")
            return plt.gcf()

        except Exception as e:
            logger.error(f"Erro ao criar gráfico sem dados: {e}", exc_info=True)
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.text(0.5, 0.5, "Erro ao criar gráfico", ha='center', va='center')
            ax.axis('off')
            return fig
