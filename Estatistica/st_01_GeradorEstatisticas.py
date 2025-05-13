import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import squarify


class GeradorEstatisticas:
    def __init__(self, db_path, localizador=None, interface_principal=None):
        self.db_path = db_path
        self.loc = localizador
        self.interface = interface_principal
        plt.style.use('bmh')

        self.atualizar_textos_traduzidos()

        if self.loc and hasattr(self.loc, 'idioma_alterado'):
            self.loc.idioma_alterado.connect(self.atualizar_textos_traduzidos)

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

    def atualizar_textos_traduzidos(self):
        gerenciador_cores = None

        if self.interface and hasattr(self.interface, 'gerenciador_menus_ui') and hasattr(self.interface.gerenciador_menus_ui, 'gerenciador_cores'):
            gerenciador_cores = self.interface.gerenciador_menus_ui.gerenciador_cores

        if gerenciador_cores:
            self.cores_operacoes = {
                self.loc.get_text("op_renamed") if self.loc else 'Renomeado': gerenciador_cores.obter_cor_hex("op_renamed"),
                self.loc.get_text("op_added") if self.loc else 'Adicionado': gerenciador_cores.obter_cor_hex("op_added"),
                self.loc.get_text("op_deleted") if self.loc else 'Excluído': gerenciador_cores.obter_cor_hex("op_deleted"),
                self.loc.get_text("op_modified") if self.loc else 'Modificado': gerenciador_cores.obter_cor_hex("op_modified"),
                self.loc.get_text("op_moved") if self.loc else 'Movido': gerenciador_cores.obter_cor_hex("op_moved"),
                self.loc.get_text("op_scanned") if self.loc else 'Escaneado': gerenciador_cores.obter_cor_hex("op_scanned"),
            }

            print(f"Cores atualizadas do gerenciador: {self.cores_operacoes}")

        else:
            self.cores_operacoes = {
                self.loc.get_text("op_renamed") if self.loc else 'Renomeado': '#00ff00',
                self.loc.get_text("op_added") if self.loc else 'Adicionado': '#0000ff',
                self.loc.get_text("op_deleted") if self.loc else 'Excluído': '#ff0000',
                self.loc.get_text("op_modified") if self.loc else 'Modificado': '#ff6200',
                self.loc.get_text("op_moved") if self.loc else 'Movido': '#ff00ff',
                self.loc.get_text("op_scanned") if self.loc else 'Escaneado': '#808080',
            }

            print("Usando cores padrão para gráficos (sem acesso ao gerenciador)")

    def _obter_dados(self):
        query = """
            SELECT tipo_operacao, tipo, timestamp, tamanho 
            FROM monitoramento 
            WHERE timestamp IS NOT NULL
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)

        if self.loc:
            mapeamento_operacoes = {
                "Added": self.loc.get_text("op_added"),
                "Deleted": self.loc.get_text("op_deleted"),
                "Modified": self.loc.get_text("op_modified"),
                "Renamed": self.loc.get_text("op_renamed"),
                "Moved": self.loc.get_text("op_moved"),
                "Scanned": self.loc.get_text("op_scanned"),
                "Adicionado": self.loc.get_text("op_added"),
                "Excluído": self.loc.get_text("op_deleted"),
                "Modificado": self.loc.get_text("op_modified"),
                "Renomeado": self.loc.get_text("op_renamed"),
                "Movido": self.loc.get_text("op_moved"),
                "Escaneado": self.loc.get_text("op_scanned"),
                "Añadido": self.loc.get_text("op_added"),
                "Eliminado": self.loc.get_text("op_deleted"),
                "Modificado": self.loc.get_text("op_modified"),
                "Renombrado": self.loc.get_text("op_renamed"),
                "Movido": self.loc.get_text("op_moved"),
                "Escaneado": self.loc.get_text("op_scanned"),
                "Ajouté": self.loc.get_text("op_added"),
                "Supprimé": self.loc.get_text("op_deleted"),
                "Modifié": self.loc.get_text("op_modified"),
                "Renommé": self.loc.get_text("op_renamed"),
                "Déplacé": self.loc.get_text("op_moved"),
                "Numérisé": self.loc.get_text("op_scanned"),
                "Aggiunto": self.loc.get_text("op_added"),
                "Eliminato": self.loc.get_text("op_deleted"),
                "Modificato": self.loc.get_text("op_modified"),
                "Rinominato": self.loc.get_text("op_renamed"),
                "Spostato": self.loc.get_text("op_moved"),
                "Scansionato": self.loc.get_text("op_scanned"),
                "Hinzugefügt": self.loc.get_text("op_added"),
                "Gelöscht": self.loc.get_text("op_deleted"),
                "Geändert": self.loc.get_text("op_modified"),
                "Umbenannt": self.loc.get_text("op_renamed"),
                "Verschoben": self.loc.get_text("op_moved"),
                "Gescannt": self.loc.get_text("op_scanned")
            }

            # Espanhol
            mapeamento_operacoes.update({
                "Añadido": self.loc.get_text("op_added"),
                "Eliminado": self.loc.get_text("op_deleted"),
                "Modificado": self.loc.get_text("op_modified"),
                "Renombrado": self.loc.get_text("op_renamed"),
                "Movido": self.loc.get_text("op_moved"),
                "Escaneado": self.loc.get_text("op_scanned")
            })

            # Francês
            mapeamento_operacoes.update({
                "Ajouté": self.loc.get_text("op_added"),
                "Supprimé": self.loc.get_text("op_deleted"),
                "Modifié": self.loc.get_text("op_modified"),
                "Renommé": self.loc.get_text("op_renamed"),
                "Déplacé": self.loc.get_text("op_moved"),
                "Numérisé": self.loc.get_text("op_scanned")
            })

            # Italiano
            mapeamento_operacoes.update({
                "Aggiunto": self.loc.get_text("op_added"),
                "Eliminato": self.loc.get_text("op_deleted"),
                "Modificato": self.loc.get_text("op_modified"),
                "Rinominato": self.loc.get_text("op_renamed"),
                "Spostato": self.loc.get_text("op_moved"),
                "Scansionato": self.loc.get_text("op_scanned")
            })

            # Alemão
            mapeamento_operacoes.update({
                "Hinzugefügt": self.loc.get_text("op_added"),
                "Gelöscht": self.loc.get_text("op_deleted"),
                "Geändert": self.loc.get_text("op_modified"),
                "Umbenannt": self.loc.get_text("op_renamed"),
                "Verschoben": self.loc.get_text("op_moved"),
                "Gescannt": self.loc.get_text("op_scanned")
            })

            df['tipo_operacao'] = df['tipo_operacao'].map(lambda x: mapeamento_operacoes.get(x, x))

            mapeamento_tipos = {
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

            df['tipo'] = df['tipo'].map(lambda x: mapeamento_tipos.get(x, x))

        return df

    def _criar_grafico_sem_dados(self, titulo):
        plt.figure(figsize=(12, 6))
        plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados para exibir', 
                 horizontalalignment='center',
                 verticalalignment='center')

        plt.title(titulo)
        plt.axis('off')

        return plt.gcf()

    def grafico_operacoes_pizza(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("operations_pie") if self.loc else 'Distribuição de Operações'

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        plt.figure(figsize=(10, 8))
        contagem = df['tipo_operacao'].value_counts()

        if not contagem.empty:
            cores = [self.cores_operacoes.get(op, '#333333') for op in contagem.index]
            plt.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=cores)
            plt.title(titulo)

        return plt.gcf()

    def grafico_tipos_arquivo_barras(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("file_types") if self.loc else 'Top 30 Tipos de Arquivo'

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        contagem = df['tipo'].value_counts()[:30]

        if not contagem.empty:
            max_label_len = max([len(str(x)) for x in contagem.index])

            fig_width = max(12, max_label_len * 0.3)

            fig_height = 6 + (len(contagem) > 15) * 2

            fig, ax = plt.subplots(figsize=(fig_width, fig_height))

            sns.barplot(x=contagem.index, y=contagem.values, ax=ax)

            plt.xticks(rotation=90, ha='right')

            ax.set_title(titulo)

            ax.set_xlabel(self.loc.get_text("type") if self.loc else 'Tipo', labelpad=10)
            ax.set_ylabel(self.loc.get_text("quantity") if self.loc else 'Quantidade')

            bottom_margin = min(0.35, max_label_len * 0.015) + 0.1

            plt.subplots_adjust(bottom=bottom_margin)

            fig.tight_layout(pad=1.2, h_pad=None, w_pad=None, rect=[0, 0.05, 1, 0.95])

        return plt.gcf()

    def grafico_timeline_operacoes(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("timeline") if self.loc else 'Timeline de Operações'

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        plt.figure(figsize=(12, 6))

        operacoes = df['tipo_operacao'].unique()
        if len(operacoes) > 0:
            for op in operacoes:
                op_data = df[df['tipo_operacao'] == op]
                if not op_data.empty:
                    plt.scatter(op_data['timestamp'], 
                            [op] * len(op_data), 
                            label=op, 
                            alpha=0.6,
                            color=self.cores_operacoes.get(op, '#333333'))

            plt.legend()

        plt.title(titulo)
        plt.xlabel(self.loc.get_text("date_time") if self.loc else 'Data/Hora')
        plt.ylabel(self.loc.get_text("operation_type") if self.loc else 'Tipo de Operação')

        return plt.gcf()

    def grafico_treemap_tipos(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("tree_map") if self.loc else 'Mapa de Árvore - Tipos de Arquivo'
        
        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        tipos = df['tipo'].value_counts()[:30]
        if not tipos.empty:
            plt.figure(figsize=(12, 8))
            squarify.plot(sizes=tipos.values, label=tipos.index, alpha=0.6)
            plt.title(titulo)
            plt.axis('off')

        return plt.gcf()

    def grafico_histograma_horarios(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("hour_histogram") if self.loc else 'Distribuição de Operações por Hora'

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        df['hora'] = pd.to_datetime(df['timestamp']).dt.hour
        plt.figure(figsize=(12, 6))
        sns.histplot(data=df, x='hora', bins=24)
        plt.title(titulo)
        plt.xlabel(self.loc.get_text("hour_of_day") if self.loc else 'Hora do Dia')
        plt.ylabel(self.loc.get_text("quantity") if self.loc else 'Quantidade')

        return plt.gcf()

    def grafico_pareto_operacoes(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("pareto_analysis") if self.loc else 'Análise de Pareto - Operações'

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        contagem = df['tipo_operacao'].value_counts()
        if not contagem.empty:
            freq_cum = contagem.cumsum() / contagem.sum() * 100

            fig, ax1 = plt.subplots(figsize=(12, 6))
            ax2 = ax1.twinx()

            cores = [self.cores_operacoes.get(op, '#333333') for op in contagem.index]
            ax1.bar(range(len(contagem)), contagem.values, color=cores)
            ax2.plot(range(len(contagem)), freq_cum, 'r-', marker='o')

            ax1.set_xticks(range(len(contagem)))
            ax1.set_xticklabels(contagem.index, rotation=45)

            ax1.set_ylabel(self.loc.get_text("quantity") if self.loc else 'Quantidade')
            ax2.set_ylabel(self.loc.get_text("cumulative_percentage") if self.loc else 'Porcentagem Acumulada')
            plt.title(titulo)

        return plt.gcf()

    def grafico_cluster_linha(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("operations_by_day") if self.loc else 'Operações por Dia'

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        df['data'] = pd.to_datetime(df['timestamp']).dt.date
        ops_por_dia = pd.crosstab(df['data'], df['tipo_operacao'])

        if not ops_por_dia.empty:
            total_por_dia = ops_por_dia.sum(axis=1)

            fig, ax1 = plt.subplots(figsize=(12, 6))
            ax2 = ax1.twinx()

            cores = {col: self.cores_operacoes.get(col, '#333333') for col in ops_por_dia.columns}
            ops_por_dia.plot(kind='bar', ax=ax1, width=0.8, color=cores, legend=False)

            ax2.plot(range(len(total_por_dia)), total_por_dia, 'r-', linewidth=2)

            ax1.set_title(titulo)
            ax1.set_xlabel(self.loc.get_text("date") if self.loc else 'Data')
            ax1.set_ylabel(self.loc.get_text("quantity_by_type") if self.loc else 'Quantidade por Tipo')
            ax2.set_ylabel(self.loc.get_text("total_operations") if self.loc else 'Total de Operações')

            handles, labels = ax1.get_legend_handles_labels()
            if handles and labels:
                ax1.legend(handles, labels)

            plt.xticks(rotation=45)
            plt.tight_layout()

        return plt.gcf()

    def salvar_graficos(self, diretorio):
        import os
        import logging
        logger = logging.getLogger('FileManager')

        graficos = {
            self.loc.get_text("operations_pie"): self.grafico_operacoes_pizza,
            self.loc.get_text("file_types"): self.grafico_tipos_arquivo_barras,
            self.loc.get_text("timeline"): self.grafico_timeline_operacoes,
            self.loc.get_text("tree_map"): self.grafico_treemap_tipos,
            self.loc.get_text("hour_histogram"): self.grafico_histograma_horarios,
            self.loc.get_text("pareto_analysis"): self.grafico_pareto_operacoes,
            self.loc.get_text("operations_by_day"): self.grafico_cluster_linha
        }

        resultados = {}

        if not os.path.exists(diretorio):
            try:
                os.makedirs(diretorio, exist_ok=True)
                logger.info(f"Diretório {diretorio} criado com sucesso")

            except Exception as e:
                logger.error(f"Erro ao criar diretório {diretorio}: {e}")
                return {nome: False for nome in graficos.keys()}

        if not os.access(diretorio, os.W_OK):
            logger.error(f"Sem permissão de escrita no diretório {diretorio}")
            return {nome: False for nome in graficos.keys()}

        for nome, func in graficos.items():
            try:
                logger.debug(f"Gerando gráfico {nome}...")
                fig = func()

                arquivo_destino = os.path.join(diretorio, f"{nome}.png")
                logger.debug(f"Salvando {nome} em {arquivo_destino}")

                try:
                    fig.savefig(arquivo_destino, bbox_inches='tight', dpi=100)
                    logger.info(f"Gráfico {nome} salvo com sucesso")
                    resultados[nome] = True

                except Exception as e:
                    logger.error(f"Erro ao salvar {nome}: {e}")
                    resultados[nome] = False

                finally:
                    plt.close(fig)
                    plt.clf()
                    plt.cla()

            except Exception as e:
                logger.error(f"Erro ao processar gráfico {nome}: {e}")
                resultados[nome] = False

        plt.close('all')

        return resultados
