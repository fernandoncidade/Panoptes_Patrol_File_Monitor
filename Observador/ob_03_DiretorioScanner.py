import queue
import threading
from concurrent.futures import ThreadPoolExecutor
from PySide6.QtCore import QObject, Signal, QMetaObject, Qt

from Observador.GerenciamentoDiretorioScanner.gscanner_01_process_batch import _process_batch
from Observador.GerenciamentoDiretorioScanner.gscanner_02_scan_directory import scan_directory
from Observador.GerenciamentoDiretorioScanner.gscanner_03_processar_fila import _processar_fila
from Observador.GerenciamentoDiretorioScanner.gscanner_04_get_file_type import get_file_type
from Observador.GerenciamentoDiretorioScanner.gscanner_05_processar_item import _processar_item
from Observador.GerenciamentoDiretorioScanner.gscanner_06_atualizar_progresso import _atualizar_progresso
from Observador.GerenciamentoDiretorioScanner.gscanner_07_atualizar_interface import _atualizar_interface
from Observador.GerenciamentoDiretorioScanner.gscanner_08_finalizar_scan import _finalizar_scan
from Observador.GerenciamentoDiretorioScanner.gscanner_09_scan_worker_run import run as scan_worker_run


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

    _process_batch = _process_batch
    scan_directory = scan_directory
    _processar_fila = _processar_fila
    get_file_type = get_file_type
    _processar_item = _processar_item
    _atualizar_progresso = _atualizar_progresso
    _atualizar_interface = _atualizar_interface
    _finalizar_scan = _finalizar_scan


class ScanWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, scanner, directory):
        super().__init__()
        self.scanner = scanner
        self.directory = directory

    run = scan_worker_run
