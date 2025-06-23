import os
import time
import win32file
import win32con
import threading
from PySide6.QtCore import QThread
from .ob_02_BaseEvento import BaseEvento
from .ob_03_DiretorioScanner import ScanWorker
from .ob_04_EventoAdicionado import EventoAdicionado
from .ob_05_EventoExcluido import EventoExcluido
from .ob_06_EventoModificado import EventoModificado
from .ob_07_EventoRenomeado import EventoRenomeado
from .ob_10_GerenciadorColunas import GerenciadorColunas
from GerenciamentoUI.ui_12_Localizador import Localizador

if not hasattr(win32con, 'FILE_NOTIFY_CHANGE_CREATION'):
    win32con.FILE_NOTIFY_CHANGE_CREATION = 0x00000040


class Observador:
    def __init__(self, diretorio, callback):
        self.diretorio = diretorio
        self.callback = callback
        self.ativo = False
        self.desligando = False
        self.thread = None
        self.ultimo_evento = None
        self.eventos_pendentes = {}
        self.registros_anteriores = {}
        self.eventos_ignorados = set()
        self.arquivos_recem_adicionados = {}
        self.arquivos_recem_excluidos = {}
        self.arquivos_recem_renomeados = {}
        self.ultima_modificacao = {}
        self._lock = threading.Lock()
        self.loc = Localizador()
        self.falhas_consecutivas = 0
        self.max_falhas = 3
        self.ultimo_erro = None

        self.interface = None
        self.gerenciador_colunas = GerenciadorColunas(self)

        self.evento_base = BaseEvento(self)
        self.evento_adicionado = EventoAdicionado(self)
        self.evento_excluido = EventoExcluido(self)
        self.evento_modificado = EventoModificado(self)
        self.evento_renomeado = EventoRenomeado(self)

        self.ACOES = {
            1: self.loc.get_text("op_added"),
            2: self.loc.get_text("op_deleted"),
            3: self.loc.get_text("op_modified"),
            4: self.loc.get_text("op_renamed"),
            5: self.loc.get_text("op_renamed")
        }

    def iniciar(self):
        with self._lock:
            if not self.ativo:
                self.ativo = True
                self.desligando = False

                self.thread_scan = QThread()
                self.scan_worker = ScanWorker(self.evento_adicionado, self.diretorio)
                self.scan_worker.moveToThread(self.thread_scan)

                self.thread_scan.started.connect(self.scan_worker.run)
                self.scan_worker.finished.connect(self.iniciar_monitoramento)
                self.scan_worker.error.connect(self.handle_scan_error)
                self.scan_worker.finished.connect(self.thread_scan.quit)
                self.scan_worker.finished.connect(self.scan_worker.deleteLater)
                self.thread_scan.finished.connect(self.thread_scan.deleteLater)

                self.thread_scan.start()

    def handle_scan_error(self, error_msg):
        print(f"Erro durante escaneamento: {error_msg}")
        self.ativo = False
        if hasattr(self, 'interface'):
            self.interface.rotulo_resultado.setText(f"Erro: {error_msg}")

    def iniciar_monitoramento(self):
        try:
            self.thread = threading.Thread(target=self.monitorar)
            self.thread.daemon = True
            self.thread.start()

            if hasattr(self, 'interface') and hasattr(self.interface, 'gerenciador_tabela'):
                self.interface.gerenciador_tabela.atualizar_dados_tabela(self.interface.tabela_dados)

                from Observador.ob_08_EventoMovido import _atualizar_contador_eventos
                _atualizar_contador_eventos(self.interface)

            if hasattr(self, 'interface'):
                self.interface.rotulo_resultado.setText(self.interface.loc.get_text("monitoring_started"))
                self.interface.atualizar_status()

        except Exception as e:
            print(f"Erro ao iniciar monitoramento: {e}")

    def parar(self):
        with self._lock:
            if not self.ativo:
                return

            self.desligando = True
            self.ativo = False

            if self.thread:
                try:
                    win32file.CancelIo(self.handle_dir)
                    self.thread.join(timeout=0.05)

                    if hasattr(self, 'handle_dir'):
                        win32file.CloseHandle(self.handle_dir)
                        del self.handle_dir

                except Exception as e:
                    print(f"Erro ao parar a thread: {e}")

            self.limpar_estado()
            self.desligando = False

    def limpar_estado(self):
        self.eventos_pendentes.clear()
        self.registros_anteriores.clear()
        self.eventos_ignorados.clear()
        self.arquivos_recem_adicionados.clear()
        self.arquivos_recem_excluidos.clear()
        self.ultima_modificacao.clear()

    def monitorar(self):
        BUFFER_SIZE = 3221225472
        FILE_LIST_DIRECTORY = 0x0001

        try:
            self.handle_dir = None
            self.handle_dir = win32file.CreateFile(
                self.diretorio,                         # caminho do diretório pai
                FILE_LIST_DIRECTORY,                    # permissão para listar diretório
                win32con.FILE_SHARE_READ |              # permitir compartilhamento de leitura
                win32con.FILE_SHARE_WRITE |             # permitir compartilhamento de escrita
                win32con.FILE_SHARE_DELETE,             # permitir compartilhamento de deleção
                None,                                   # sem atributos de segurança
                win32con.OPEN_EXISTING,                 # abrir diretório existente
                win32con.FILE_FLAG_BACKUP_SEMANTICS |   # necessário para monitorar diretórios
                win32con.FILE_FLAG_OVERLAPPED,          # permite operações assíncronas
                None                                    # sem template
            )

        except Exception as e:
            print(f"Erro ao criar handle de diretório: {e}")
            self.handle_dir = None
            return

        while self.ativo:
            try:
                results = win32file.ReadDirectoryChangesW(
                    self.handle_dir,
                    BUFFER_SIZE,
                    True,                                       # monitorar subdiretórios recursivamente
                    win32con.FILE_NOTIFY_CHANGE_FILE_NAME |     # mudanças em nomes de arquivos
                    win32con.FILE_NOTIFY_CHANGE_DIR_NAME |      # mudanças em nomes de diretórios
                    win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |    # mudanças de atributos
                    win32con.FILE_NOTIFY_CHANGE_SIZE |          # mudanças de tamanho
                    win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |    # mudanças na última escrita
                    win32con.FILE_NOTIFY_CHANGE_SECURITY |      # mudanças de segurança
                    win32con.FILE_NOTIFY_CHANGE_CREATION,       # criação de arquivos/pastas
                    None,
                    None
                )

                for action, file in results:
                    self.processar_evento(action, file)

            except win32file.error as e:
                if self.desligando:
                    break

                print(f"Erro no monitoramento: {e}")

            except Exception as e:
                print(f"Erro desconhecido: {e}")

        try:
            if hasattr(self, 'handle_dir') and self.handle_dir is not None:
                win32file.CloseHandle(self.handle_dir)
                self.handle_dir = None

        except Exception as e:
            print(f"Erro ao fechar handle de diretório: {e}")

    def processar_evento(self, acao, nome_arquivo):
        try:
            if self.falhas_consecutivas >= self.max_falhas:
                print("Muitas falhas consecutivas, reiniciando monitoramento...")
                self.reiniciar_monitoramento()
                return

            caminho_completo = os.path.join(self.diretorio, nome_arquivo)
            tempo_atual = time.time()

            if nome_arquivo in self.eventos_ignorados:
                self.eventos_ignorados.remove(nome_arquivo)
                return

            if acao == 3 and os.path.isdir(caminho_completo):
                return

            if acao == 2:
                if nome_arquivo in self.arquivos_recem_adicionados:
                    if (tempo_atual - self.arquivos_recem_adicionados[nome_arquivo]) < 1:
                        return

                self.evento_excluido.processar(nome_arquivo, caminho_completo, tempo_atual)
                return

            elif acao in [4, 5]:
                self.evento_renomeado.processar(nome_arquivo, caminho_completo, acao)
                return

            elif acao == 1:
                if nome_arquivo in self.arquivos_recem_adicionados:
                    if (tempo_atual - self.arquivos_recem_adicionados[nome_arquivo]) < 1:
                        return

                self.arquivos_recem_adicionados[nome_arquivo] = tempo_atual
                self.evento_adicionado.processar(nome_arquivo, caminho_completo, tempo_atual)
                return

            elif acao == 3:
                if os.path.exists(caminho_completo):
                    self.evento_modificado.processar(nome_arquivo, caminho_completo, tempo_atual)

            self.falhas_consecutivas = 0

        except Exception as e:
            self.falhas_consecutivas += 1
            self.ultimo_erro = str(e)
            print(f"Erro ao processar evento (tentativa {self.falhas_consecutivas}): {e}")

    def reiniciar_monitoramento(self):
        try:
            self.parar()
            time.sleep(2)
            self.falhas_consecutivas = 0
            self.iniciar()

        except Exception as e:
            print(f"Erro ao reiniciar monitoramento: {e}")
