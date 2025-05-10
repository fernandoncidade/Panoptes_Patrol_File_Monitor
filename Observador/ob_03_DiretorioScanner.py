import os
import queue
import threading
import sqlite3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import QObject, Signal, QMetaObject, Qt, Q_ARG


class DiretorioScanner(QObject):
    progresso_atualizado = Signal(int, int, int)
    scan_finalizado = Signal()

    def __init__(self, observador):
        super().__init__()
        self.observador = observador
        self.db_path = observador.evento_base.db_path
        self.gerenciador_colunas = observador.gerenciador_colunas
        self.fila_processamento = queue.Queue()
        self.lote_atual = []
        self.tamanho_lote = 1000000
        self.contador_processados = 0
        self.total_arquivos = 0
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.lock_db = threading.Lock()
        self.ultimo_progresso = 0
        self.intervalo_atualizacao = 1

        if hasattr(self.observador, 'interface'):
            QMetaObject.invokeMethod(self.observador.interface, "criar_barra_progresso",
                                     Qt.ConnectionType.QueuedConnection)

            self.progresso_atualizado.connect(self._atualizar_interface)
            self.scan_finalizado.connect(self._finalizar_scan)

    def _process_batch(self, batch):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for nome, caminho, _ in batch:
                    try:
                        tipo = self.get_file_type(caminho)

                        metadados = self.gerenciador_colunas.get_metadados({
                            "nome": nome,
                            "dir_atual": caminho
                        })

                        cursor.execute("""
                            INSERT INTO snapshot (
                                    nome,
                                    diretorio,
                                    tipo,
                                    data_criacao,
                                    data_modificacao,
                                    data_acesso,
                                    tamanho,
                                    atributos,
                                    autor,
                                    dimensoes,
                                    duracao,
                                    taxa_bits,
                                    protegido,
                                    timestamp
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            nome,
                            caminho,
                            tipo,
                            metadados.get("data_criacao", ""),
                            metadados.get("data_modificacao", ""),
                            metadados.get("data_acesso", ""),
                            metadados.get("tamanho", ""),
                            metadados.get("atributos", ""),
                            metadados.get("autor", ""),
                            metadados.get("dimensoes", ""),
                            metadados.get("duracao", ""),
                            metadados.get("taxa_bits", ""),
                            metadados.get("protegido", ""),
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ))

                        self.contador_processados += 1
                        if self.contador_processados % self.intervalo_atualizacao == 0:
                            self._atualizar_progresso()

                    except Exception as e:
                        print(f"Erro ao processar item {nome}: {e}")
                        continue

                conn.commit()

        except Exception as e:
            print(f"Erro ao processar lote: {e}")
            raise

    def scan_directory(self, directory):
        try:
            self.total_arquivos = 0
            for _, dirs, files in os.walk(directory):
                self.total_arquivos += len(files) + len(dirs)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM snapshot")
                conn.commit()

            batch = []
            for root, dirs, files in os.walk(directory):
                if self.observador.desligando:
                    return

                for d in dirs:
                    caminho = os.path.join(root, d)
                    batch.append((d, caminho, "Diretório"))
                    if len(batch) >= self.tamanho_lote:
                        self._process_batch(batch)
                        batch = []

                for f in files:
                    caminho = os.path.join(root, f)
                    batch.append((f, caminho, "Arquivo"))
                    if len(batch) >= self.tamanho_lote:
                        self._process_batch(batch)
                        batch = []

            if batch:
                self._process_batch(batch)

            self.scan_finalizado.emit()

        except Exception as e:
            print(f"Erro no scan_directory: {e}")
            raise

    def _processar_fila(self):
        while True:
            try:
                item, caminho, tipo = self.fila_processamento.get(timeout=1)
                self._processar_item(item, caminho, tipo)
                self.fila_processamento.task_done()
                self.contador_processados += 1

            except queue.Empty:
                break

            except Exception as e:
                print(f"Erro no processamento: {e}")
                self.fila_processamento.task_done()

    def get_file_type(self, caminho):
        if not caminho or not os.path.exists(caminho):
            return self.observador.loc.get_text("unknown")

        if os.path.isdir(caminho):
            return self.observador.loc.get_text("folder")

        ext = os.path.splitext(caminho)[1].lower()

        TIPOS_ARQUIVO = {
            '.pdf': 'pdf',
            '.doc': 'doc',
            '.docx': 'docx',
            '.dotx': 'dotx',
            '.docm': 'docm',
            '.dotm': 'dotm',
            '.xls': 'xls', 
            '.xlsx': 'xlsx',
            '.xlsm': 'xlsm',
            '.xltx': 'xltx',
            '.xltm': 'xltm',
            '.ppt': 'ppt',
            '.pptx': 'pptx',
            '.potx': 'potx',
            '.ppsx': 'ppsx',
            '.mdb': 'mdb',
            '.accdb': 'accdb',
            '.msg': 'msg',
            '.pst': 'pst',
            '.ost': 'ost',
            '.pub': 'pub',
            '.vsd': 'vsd',
            '.vsdx': 'vsdx',
            '.mpp': 'mpp',
            '.mpt': 'mpt',
            '.txt': 'txt',
            '.rtf': 'rtf',
            '.csv': 'csv',
            '.log': 'log',
            '.tmp': 'tmp',
            '.temp': 'temp',
            '.bak': 'bak',
            '.swp': 'swp',
            '.swo': 'swo',
            '.old': 'old',
            '.part': 'part',

            # Imagens
            '.jpg': 'jpg',
            '.jpeg': 'jpeg',
            '.png': 'png',
            '.gif': 'gif',
            '.bmp': 'bmp',
            '.tiff': 'tiff',
            '.tif': 'tif',
            '.webp': 'webp',
            '.svg': 'svg',
            '.psd': 'psd',
            '.raw': 'raw',
            '.heic': 'heic',
            '.heif': 'heif',
            '.cr2': 'cr2',
            '.nef': 'nef',
            '.arw': 'arw',

            # Áudios
            '.mp3': 'mp3',
            '.wav': 'wav',
            '.wma': 'wma',
            '.aac': 'aac',
            '.ogg': 'ogg',
            '.flac': 'flac',
            '.m4a': 'm4a',
            '.aiff': 'aiff',
            '.aif': 'aif',

            # Vídeos
            '.mp4': 'mp4',
            '.avi': 'avi',
            '.mkv': 'mkv',
            '.mov': 'mov',
            '.wmv': 'wmv',
            '.flv': 'flv',
            '.webm': 'webm',
            '.mts': 'mts',
            '.m2ts': 'm2ts',
            '.mpeg': 'mpeg',
            '.m4v': 'm4v',

            # Compactados
            '.zip': 'zip',
            '.rar': 'rar',
            '.7z': '7z',
            '.tar': 'tar',
            '.gz': 'gz',
            '.bz2': 'bz2',
            '.xz': 'xz',
            '.cab': 'cab',

            # Executáveis
            '.exe': 'exe',
            '.msi': 'msi',
            '.bat': 'bat',

            # Código fonte
            '.py': 'py',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'h',
            '.hpp': 'hpp',
            '.cs': 'cs',
            '.js': 'js',
            '.html': 'html',
            '.htm': 'htm',
            '.mht': 'mht',
            '.xhtml': 'xhtml',
            '.mhml': 'mhml',
            '.css': 'css',
            '.php': 'php',
            '.sql': 'sql',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yml',
            '.ini': 'ini',
            '.cfg': 'cfg',
            '.conf': 'conf',
            '.log': 'log',
            '.md': 'md',
            '.rst': 'rst',
            '.bat': 'bat',
            '.sh': 'sh',
            '.ps1': 'ps1',
            '.psm1': 'psm1',
            '.psd1': 'psd1',
            '.ps1xml': 'ps1xml',
            '.pssc': 'pssc',
            '.psc1': 'psc1'
        }

        return TIPOS_ARQUIVO.get(ext, ext[1:].upper() if ext else self.observador.loc.get_text("unknown"))

    def _processar_item(self, nome, caminho, tipo):
        try:
            metadados = self.gerenciador_colunas.get_metadados({
                "nome": nome,
                "dir_atual": caminho
            })

            tipo = self.get_file_type(caminho)

            with self.lock_db:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO snapshot 
                        (nome, diretorio, tipo, data_criacao, data_modificacao, 
                        data_acesso, tamanho, atributos, autor, dimensoes,
                        duracao, taxa_bits, protegido, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        nome,
                        caminho,
                        tipo,
                        metadados.get("data_criacao", ""),
                        metadados.get("data_modificacao", ""),
                        metadados.get("data_acesso", ""),
                        metadados.get("tamanho", ""),
                        metadados.get("atributos", ""),
                        metadados.get("autor", ""),
                        metadados.get("dimensoes", ""),
                        metadados.get("duracao", ""),
                        metadados.get("taxa_bits", ""),
                        metadados.get("protegido", ""),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))

                    conn.commit()

        except Exception as e:
            print(f"Erro ao processar item {nome}: {e}")

    def _atualizar_progresso(self):
        if hasattr(self.observador, 'interface'):
            progresso = (self.contador_processados / self.total_arquivos) * 100 if self.total_arquivos > 0 else 0
            if abs(progresso - self.ultimo_progresso) >= 1:
                self.ultimo_progresso = progresso
                self.progresso_atualizado.emit(int(progresso), self.contador_processados, self.total_arquivos)

    def _atualizar_interface(self, progresso, contador, total):
        try:
            if not hasattr(self.observador, 'interface'):
                return

            QMetaObject.invokeMethod(self.observador.interface,
                                     "atualizar_progresso_scan",
                                     Qt.ConnectionType.QueuedConnection,
                                     Q_ARG(int, progresso),
                                     Q_ARG(int, contador),
                                     Q_ARG(int, total))

        except Exception as e:
            print(f"Erro ao atualizar interface: {e}")

    def _finalizar_scan(self):
        if hasattr(self.observador, 'interface') and hasattr(self.observador.interface, 'barra_progresso'):
            self.observador.interface.barra_progresso.hide()
            self.observador.interface.barra_progresso.setValue(0)

            if hasattr(self.observador.interface, 'gerenciador_tabela'):
                self.observador.interface.gerenciador_tabela.atualizar_dados_tabela(self.observador.interface.tabela_dados)

                from Observador.ob_08_EventoMovido import _atualizar_contador_eventos
                _atualizar_contador_eventos(self.observador.interface)
                self.observador.interface.atualizar_status()


class ScanWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, scanner, directory):
        super().__init__()
        self.scanner = scanner
        self.directory = directory

    def run(self):
        try:
            self.scanner.scan_directory(self.directory)
            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))
