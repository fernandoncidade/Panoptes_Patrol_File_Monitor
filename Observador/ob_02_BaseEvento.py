import os
import sys
import sqlite3
import win32file
import win32con
from datetime import datetime

def obter_caminho_persistente():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        config_dir = os.path.join(base_path, "config")
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)

            except Exception as e:
                print(f"Erro ao criar diretório de configuração: {e}")

        return config_dir

    else:
        return os.path.dirname(__file__)


class BaseEvento:
    def __init__(self, observador):
        self.observador = observador
        self.db_path = os.path.join(obter_caminho_persistente(), "monitoramento.db")
        print(f"Caminho do banco de dados: {self.db_path}")

        self.criar_banco_de_dados()

        self.operacoes = {
            self.observador.loc.get_text("op_renamed"): self.observador.loc.get_text("op_renamed"),
            self.observador.loc.get_text("op_added"): self.observador.loc.get_text("op_added"),
            self.observador.loc.get_text("op_deleted"): self.observador.loc.get_text("op_deleted"),
            self.observador.loc.get_text("op_modified"): self.observador.loc.get_text("op_modified"),
            self.observador.loc.get_text("op_moved"): self.observador.loc.get_text("op_moved"),
            self.observador.loc.get_text("op_scanned"): self.observador.loc.get_text("op_scanned")
        }

        self.eventos_excluidos = 0
        self.callback = None

    def set_callback(self, callback):
        self.callback = callback

    def criar_banco_de_dados(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            tabelas_eventos = ['monitoramento', 'adicionado', 'excluido', 'modificado', 'renomeado', 'movido', 'escaneado']
            colunas_padrao = [
                ("tipo_operacao", "TEXT"),
                ("nome", "TEXT"),
                ("dir_anterior", "TEXT"),
                ("dir_atual", "TEXT"),
                ("data_criacao", "TEXT"),
                ("data_modificacao", "TEXT"),
                ("data_acesso", "TEXT"),
                ("tipo", "TEXT"),
                ("tamanho", "TEXT"),
                ("atributos", "TEXT"),
                ("autor", "TEXT"),
                ("dimensoes", "TEXT"),
                ("duracao", "TEXT"),
                ("taxa_bits", "TEXT"),
                ("protegido", "TEXT"),
                ("paginas", "TEXT"),
                ("linhas", "TEXT"),
                ("palavras", "TEXT"),
                ("paginas_estimadas", "TEXT"),
                ("linhas_codigo", "TEXT"),
                ("total_linhas", "TEXT"),
                ("slides_estimados", "TEXT"),
                ("arquivos", "TEXT"),
                ("descompactados", "TEXT"),
                ("slides", "TEXT"),
                ("binario", "TEXT"),
                ("planilhas", "TEXT"),
                ("colunas", "TEXT"),
                ("registros", "TEXT"),
                ("tabelas", "TEXT"),
                ("timestamp", "TEXT")
            ]

            for tabela in tabelas_eventos:
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS {tabela} (id INTEGER PRIMARY KEY AUTOINCREMENT)""")
                cursor.execute(f"PRAGMA table_info({tabela})")
                existentes = [col[1] for col in cursor.fetchall()]
                for col_nome, col_tipo in colunas_padrao:
                    if col_nome not in existentes:
                        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN {col_nome} {col_tipo}")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS snapshot (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    diretorio TEXT,
                    tipo TEXT,
                    data_criacao TEXT,
                    data_modificacao TEXT,
                    data_acesso TEXT,
                    tamanho TEXT,
                    atributos TEXT,
                    autor TEXT,
                    dimensoes TEXT,
                    duracao TEXT,
                    taxa_bits TEXT,
                    protegido TEXT,
                    paginas TEXT,
                    linhas TEXT,
                    palavras TEXT,
                    paginas_estimadas TEXT,
                    linhas_codigo TEXT,
                    total_linhas TEXT,
                    slides_estimados TEXT,
                    arquivos TEXT,
                    descompactados TEXT,
                    slides TEXT,
                    binario TEXT,
                    planilhas TEXT,
                    colunas TEXT,
                    registros TEXT,
                    tabelas TEXT,
                    timestamp TEXT
                )
            """)

            for tabela in tabelas_eventos + ['snapshot']:
                cursor.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{tabela}_nome 
                    ON {tabela} (nome)
                """)

                if tabela == 'snapshot':
                    cursor.execute(f"""
                        CREATE INDEX IF NOT EXISTS idx_{tabela}_diretorio 
                        ON {tabela} (diretorio)
                    """)

                else:
                    cursor.execute(f"""
                        CREATE INDEX IF NOT EXISTS idx_{tabela}_dirs 
                        ON {tabela} (dir_anterior, dir_atual)
                    """)

            cursor.execute("CREATE INDEX IF NOT EXISTS idx_monitoramento_nome_id ON monitoramento(nome, id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshot_nome_timestamp ON snapshot(nome, timestamp)")

            cursor.execute("PRAGMA journal_mode = WAL")
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA temp_store = MEMORY")

            cursor.execute("PRAGMA cache_size = 100000")
            cursor.execute("PRAGMA page_size = 16384")
            cursor.execute("PRAGMA mmap_size = 4294967296")

            conn.commit()

    def processar_exclusao(self, evento):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                query = """
                    SELECT 
                        m.tipo_operacao,
                        m.nome,
                        m.dir_anterior,
                        m.dir_atual,
                        m.data_criacao,
                        m.data_modificacao,
                        m.data_acesso,
                        m.tipo,
                        m.tamanho,
                        m.atributos,
                        m.autor,
                        m.dimensoes,
                        m.duracao, 
                        m.taxa_bits,
                        m.protegido,
                        m.paginas,
                        m.linhas,
                        m.palavras,
                        m.paginas_estimadas,
                        m.linhas_codigo,
                        m.total_linhas,
                        m.slides_estimados,
                        m.arquivos,
                        m.descompactados,
                        m.slides,
                        m.binario,
                        m.planilhas,
                        m.colunas,
                        m.registros,
                        m.tabelas,
                        m.timestamp
                    FROM monitoramento m
                    WHERE m.nome = ?

                    UNION ALL

                    SELECT 
                        NULL as tipo_operacao,
                        s.nome,
                        s.diretorio as dir_anterior,
                        s.diretorio as dir_atual,
                        s.data_criacao,
                        s.data_modificacao,
                        s.data_acesso,
                        s.tipo,
                        s.tamanho,
                        s.atributos,
                        s.autor,
                        s.dimensoes,
                        s.duracao, 
                        s.taxa_bits,
                        s.protegido,
                        s.paginas,
                        s.linhas,
                        s.palavras,
                        s.paginas_estimadas,
                        s.linhas_codigo,
                        s.total_linhas,
                        s.slides_estimados,
                        s.arquivos,
                        s.descompactados,
                        s.slides,
                        s.binario,
                        s.planilhas,
                        s.colunas,
                        s.registros,
                        s.tabelas,
                        s.timestamp
                    FROM snapshot s
                    WHERE s.nome = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """

                cursor.execute(query, (evento.get("nome"), evento.get("nome")))
                result = cursor.fetchone()

                colunas = [
                    "tipo_operacao",
                    "nome",
                    "dir_anterior",
                    "dir_atual",
                    "data_criacao",
                    "data_modificacao",
                    "data_acesso",
                    "tipo",
                    "tamanho",
                    "atributos",
                    "autor",
                    "dimensoes",
                    "duracao", 
                    "taxa_bits",
                    "protegido",
                    "paginas",
                    "linhas",
                    "palavras",
                    "paginas_estimadas",
                    "linhas_codigo",
                    "total_linhas",
                    "slides_estimados",
                    "arquivos",
                    "descompactados",
                    "slides",
                    "binario",
                    "planilhas",
                    "colunas",
                    "registros",
                    "tabelas",
                    "timestamp"
                ]
                print(f"Processando exclusão para: {evento.get('nome')}")

                if result:
                    metadados = dict(zip(colunas, result))
                    print(f"Metadados encontrados: tipo={metadados.get('tipo')}, dir={metadados.get('dir_anterior')}")

                else:
                    metadados = {
                        "nome": evento.get("nome"),
                        "dir_anterior": evento.get("dir_anterior"),
                        "dir_atual": "",
                        "tipo": self.observador.gerenciador_colunas.identificar_tipo_arquivo(evento.get("nome")),
                        "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "data_modificacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "data_acesso": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "tamanho": "",
                        "atributos": "",
                        "autor": "",
                        "dimensoes": "",
                        "duracao": "",
                        "taxa_bits": "",
                        "protegido": "",
                        "paginas": "",
                        "linhas": "",
                        "palavras": "",
                        "paginas_estimadas": "",
                        "linhas_codigo": "",
                        "total_linhas": "",
                        "slides_estimados": "",
                        "arquivos": "",
                        "descompactados": "",
                        "slides": "",
                        "binario": "",
                        "planilhas": "",
                        "colunas": "",
                        "registros": "",
                        "tabelas": ""
                    }
                    print(f"Nenhum metadado encontrado, usando valores default. Tipo identificado: {metadados['tipo']}")

                valores = (
                    self.observador.loc.get_text("op_deleted"),
                    metadados.get("nome"),
                    evento.get("dir_anterior"),
                    "",
                    metadados.get("data_criacao"),
                    metadados.get("data_modificacao"),
                    metadados.get("data_acesso"),
                    metadados.get("tipo"),
                    metadados.get("tamanho"),
                    metadados.get("atributos"),
                    metadados.get("autor"),
                    metadados.get("dimensoes"),
                    metadados.get("duracao"),
                    metadados.get("taxa_bits"),
                    metadados.get("protegido"),
                    metadados.get("paginas", ""),
                    metadados.get("linhas", ""),
                    metadados.get("palavras", ""),
                    metadados.get("paginas_estimadas", ""),
                    metadados.get("linhas_codigo", ""),
                    metadados.get("total_linhas", ""),
                    metadados.get("slides_estimados", ""),
                    metadados.get("arquivos", ""),
                    metadados.get("descompactados", ""),
                    metadados.get("slides", ""),
                    metadados.get("binario", ""),
                    metadados.get("planilhas", ""),
                    metadados.get("colunas", ""),
                    metadados.get("registros", ""),
                    metadados.get("tabelas", ""),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                )
                cursor.execute("BEGIN TRANSACTION")

                cursor.execute("""
                    INSERT INTO excluido (
                                tipo_operacao,
                                nome,
                                dir_anterior,
                                dir_atual,
                                data_criacao,
                                data_modificacao,
                                data_acesso,
                                tipo,
                                tamanho,
                                atributos,
                                autor,
                                dimensoes,
                                duracao,
                                taxa_bits,
                                protegido,
                                paginas,
                                linhas,
                                palavras,
                                paginas_estimadas,
                                linhas_codigo,
                                total_linhas,
                                slides_estimados,
                                arquivos,
                                descompactados,
                                slides,
                                binario,
                                planilhas,
                                colunas,
                                registros,
                                tabelas,
                                timestamp
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, valores)

                cursor.execute("""
                    INSERT INTO monitoramento (
                                tipo_operacao,
                                nome,
                                dir_anterior,
                                dir_atual,
                                data_criacao,
                                data_modificacao,
                                data_acesso,
                                tipo,
                                tamanho,
                                atributos,
                                autor,
                                dimensoes,
                                duracao,
                                taxa_bits,
                                protegido,
                                paginas,
                                linhas,
                                palavras,
                                paginas_estimadas,
                                linhas_codigo,
                                total_linhas,
                                slides_estimados,
                                arquivos,
                                descompactados,
                                slides,
                                binario,
                                planilhas,
                                colunas,
                                registros,
                                tabelas,
                                timestamp
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, valores)

                cursor.execute("COMMIT")
                print(f"Registro de exclusão concluído para: {evento.get('nome')}")

                if not evento.get("_temporario", False):
                    self._atualizar_interface_apos_exclusao()

        except Exception as e:
            print(f"Erro ao processar exclusão: {e}")
            try:
                if conn:
                    cursor.execute("ROLLBACK")

            except Exception:
                pass

    def registrar_evento_especifico(self, tabela, evento):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    INSERT INTO {tabela} (
                        nome,
                        dir_anterior,
                        dir_atual,
                        data_criacao,
                        data_modificacao,
                        data_acesso,
                        tipo,
                        tamanho,
                        atributos,
                        autor,
                        dimensoes,
                        duracao,
                        taxa_bits,
                        protegido,
                        paginas,
                        linhas,
                        palavras,
                        paginas_estimadas,
                        linhas_codigo,
                        total_linhas,
                        slides_estimados,
                        arquivos,
                        descompactados,
                        slides,
                        binario,
                        planilhas,
                        colunas,
                        registros,
                        tabelas,
                        timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    evento["nome"],
                    evento.get("dir_anterior", ""),
                    evento.get("dir_atual", ""),
                    evento.get("data_criacao", ""),
                    evento.get("data_modificacao", ""),
                    evento.get("data_acesso", ""),
                    evento["tipo"],
                    evento.get("tamanho", ""),
                    evento.get("atributos", ""),
                    evento.get("autor", ""),
                    evento.get("dimensoes", ""),
                    evento.get("duracao", ""),
                    evento.get("taxa_bits", ""),
                    evento.get("protegido", ""),
                    evento.get("paginas", ""),
                    evento.get("linhas", ""),
                    evento.get("palavras", ""),
                    evento.get("paginas_estimadas", ""),
                    evento.get("linhas_codigo", ""),
                    evento.get("total_linhas", ""),
                    evento.get("slides_estimados", ""),
                    evento.get("arquivos", ""),
                    evento.get("descompactados", ""),
                    evento.get("slides", ""),
                    evento.get("binario", ""),
                    evento.get("planilhas", ""),
                    evento.get("colunas", ""),
                    evento.get("registros", ""),
                    evento.get("tabelas", ""),
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

                conn.commit()

        except Exception as e:
            print(f"Erro ao registrar evento na tabela {tabela}: {e}")

    def obter_metadados_arquivo_excluido(self, nome):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    SELECT 
                        tipo_operacao, 
                        nome, 
                        dir_anterior, 
                        dir_atual, 
                        data_criacao, 
                        data_modificacao, 
                        data_acesso, 
                        tipo, 
                        tamanho, 
                        atributos, 
                        autor, 
                        dimensoes, 
                        duracao, 
                        taxa_bits, 
                        protegido, 
                        paginas,
                        linhas,
                        palavras,
                        paginas_estimadas,
                        linhas_codigo,
                        total_linhas,
                        slides_estimados,
                        arquivos,
                        descompactados,
                        slides,
                        binario,
                        planilhas,
                        colunas,
                        registros,
                        tabelas,
                        timestamp
                    FROM monitoramento
                    WHERE nome = ?
                    ORDER BY id DESC
                    LIMIT 1
                """, (nome,))

                resultado = cursor.fetchone()
                if resultado:
                    colunas = ['tipo_operacao', 
                                'nome', 
                                'dir_anterior', 
                                'dir_atual', 
                                'data_criacao', 
                                'data_modificacao', 
                                'data_acesso', 
                                'tipo', 
                                'tamanho', 
                                'atributos', 
                                'autor', 
                                'dimensoes', 
                                'duracao', 
                                'taxa_bits', 
                                'protegido', 
                                'paginas',
                                'linhas',
                                'palavras',
                                'paginas_estimadas',
                                'linhas_codigo',
                                'total_linhas',
                                'slides_estimados',
                                'arquivos',
                                'descompactados',
                                'slides',
                                'binario',
                                'planilhas',
                                'colunas',
                                'registros',
                                'tabelas',
                                'timestamp']
                    return dict(zip(colunas, resultado))

                cursor.execute("""
                    SELECT NULL as 
                            tipo_operacao, 
                            nome, 
                            diretorio as dir_anterior, 
                            diretorio as dir_atual, 
                            data_criacao, 
                            data_modificacao, 
                            data_acesso, 
                            tipo, 
                            tamanho, 
                            atributos, 
                            autor, 
                            dimensoes, 
                            duracao, 
                            taxa_bits, 
                            protegido, 
                            paginas,
                            linhas,
                            palavras,
                            paginas_estimadas,
                            linhas_codigo,
                            total_linhas,
                            slides_estimados,
                            arquivos,
                            descompactados,
                            slides,
                            binario,
                            planilhas,
                            colunas,
                            registros,
                            tabelas,
                            timestamp
                    FROM snapshot
                    WHERE nome = ?
                    ORDER BY timestamp DESC
                    LIMIT 1
                """, (nome,))

                resultado = cursor.fetchone()
                if resultado:
                    colunas = ['tipo_operacao', 
                            'nome', 
                            'dir_anterior', 
                            'dir_atual', 
                            'data_criacao', 
                            'data_modificacao', 
                            'data_acesso',
                            'tipo', 
                            'tamanho', 
                            'atributos', 
                            'autor', 
                            'dimensoes', 
                            'duracao', 
                            'taxa_bits', 
                            'protegido', 
                            'paginas',
                            'linhas',
                            'palavras',
                            'paginas_estimadas',
                            'linhas_codigo',
                            'total_linhas',
                            'slides_estimados',
                            'arquivos',
                            'descompactados',
                            'slides',
                            'binario',
                            'planilhas',
                            'colunas',
                            'registros',
                            'tabelas',
                            'timestamp']
                    return dict(zip(colunas, resultado))

                return None

        except Exception as e:
            print(f"Erro ao buscar metadados de arquivo excluído: {e}")
            return None

    def registrar_evento_no_banco(self, evento):
        try:
            for campo_obrigatorio in ["tipo_operacao", "nome"]:
                if campo_obrigatorio not in evento:
                    print(f"Erro: Campo obrigatório '{campo_obrigatorio}' ausente no evento")
                    return

            if "dir_anterior" in evento and (not evento["dir_anterior"] or evento["dir_anterior"] == "."):
                evento["dir_anterior"] = ""

            if "dir_atual" in evento and (not evento["dir_atual"] or evento["dir_atual"] == "."):
                evento["dir_atual"] = ""

            mapeamento_tabelas = {
                self.observador.loc.get_text("op_added"): "adicionado",
                self.observador.loc.get_text("op_deleted"): "excluido",
                self.observador.loc.get_text("op_modified"): "modificado", 
                self.observador.loc.get_text("op_renamed"): "renomeado",
                self.observador.loc.get_text("op_moved"): "movido",
                self.observador.loc.get_text("op_scanned"): "escaneado"
            }

            tipo_operacao_original = evento["tipo_operacao"]
            tabela_especifica = mapeamento_tabelas.get(tipo_operacao_original)

            if not tabela_especifica:
                print(f"Erro: Tipo de operação desconhecido: {tipo_operacao_original}")
                return

            campos_opcionais = [
                "dir_anterior",
                "dir_atual",
                "data_criacao",
                "data_modificacao",
                "data_acesso",
                "tipo",
                "tamanho",
                "atributos",
                "autor",
                "dimensoes",
                "duracao",
                "taxa_bits",
                "protegido",
                "paginas",
                "linhas",
                "palavras",
                "paginas_estimadas",
                "linhas_codigo",
                "total_linhas",
                "slides_estimados",
                "arquivos",
                "descompactados",
                "slides",
                "binario",
                "planilhas",
                "colunas",
                "registros",
                "tabelas"
            ]

            for campo in campos_opcionais:
                if campo not in evento:
                    evento[campo] = ""

            if "timestamp" not in evento:
                evento["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute("BEGIN TRANSACTION")

                try:
                    colunas = [
                        "tipo_operacao",
                        "nome",
                        "dir_anterior",
                        "dir_atual",
                        "data_criacao",
                        "data_modificacao",
                        "data_acesso",
                        "tipo",
                        "tamanho",
                        "atributos",
                        "autor",
                        "dimensoes",
                        "duracao", 
                        "taxa_bits",
                        "protegido",
                        "paginas",
                        "linhas",
                        "palavras",
                        "paginas_estimadas",
                        "linhas_codigo",
                        "total_linhas",
                        "slides_estimados",
                        "arquivos",
                        "descompactados",
                        "slides",
                        "binario",
                        "planilhas",
                        "colunas",
                        "registros",
                        "tabelas",
                        "timestamp"
                    ]

                    valores = [evento.get(coluna.replace("tipo_operacao", "tipo_operacao"), "") for coluna in colunas]
                    valores[0] = tipo_operacao_original

                    placeholders = ", ".join(["?" for _ in colunas])
                    colunas_str = ", ".join(colunas)

                    query_tabela = f"INSERT INTO {tabela_especifica} ({colunas_str}) VALUES ({placeholders})"
                    cursor.execute(query_tabela, valores)

                    query_monitoramento = f"INSERT INTO monitoramento ({colunas_str}) VALUES ({placeholders})"
                    cursor.execute(query_monitoramento, valores)

                    cursor.execute("COMMIT")
                    print(f"Evento registrado com sucesso: {tipo_operacao_original} - {evento.get('nome')}")

                    self._atualizar_interface_apos_evento(evento)

                except Exception as e:
                    cursor.execute("ROLLBACK")
                    print(f"Erro durante registro de evento, transação cancelada: {e}")
                    raise

        except Exception as e:
            print(f"Erro ao registrar evento no banco: {e}")

    def _atualizar_interface_apos_evento(self, evento):
        try:
            interface = None
            if self.callback and hasattr(self.callback, '__self__'):
                interface = self.callback.__self__
            elif hasattr(self.observador, 'interface'):
                interface = self.observador.interface

            if interface and hasattr(interface, 'gerenciador_tabela'):
                interface.gerenciador_tabela.atualizar_linha_mais_recente(interface.tabela_dados)

                from Observador.ob_08_EventoMovido import _atualizar_contador_eventos
                _atualizar_contador_eventos(interface)

                interface.atualizar_status()
        except Exception as e:
            print(f"Erro ao atualizar interface após evento: {e}")

    def scan_directory(self, directory):
        try:
            from .ob_03_DiretorioScanner import DiretorioScanner
            scanner = DiretorioScanner(self.observador)
            scanner.scan_directory(directory)

        except Exception as e:
            print(f"Erro ao escanear diretório: {e}")

    def get_tipo_from_snapshot(self, nome):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tipo FROM snapshot 
                WHERE nome = ?
                LIMIT 1
            """, (nome,))

            row = cursor.fetchone()
            return row[0] if row else None

    def is_directory(self, path):
        try:
            attrs = win32file.GetFileAttributes(path)
            return attrs & win32con.FILE_ATTRIBUTE_DIRECTORY == win32con.FILE_ATTRIBUTE_DIRECTORY

        except:
            return False

    def limpar_registros(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                tabelas = [
                    'monitoramento',
                    'snapshot',
                    'adicionado',
                    'excluido',
                    'modificado',
                    'renomeado',
                    'movido',
                    'escaneado'
                    ]

                for tabela in tabelas:
                    cursor.execute(f"DELETE FROM {tabela}")
                    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{tabela}'")

                conn.commit()

            with sqlite3.connect(self.db_path, isolation_level=None) as conn:
                cursor = conn.cursor()
                cursor.execute("VACUUM")

        except Exception as e:
            print(f"Erro ao limpar registros do banco: {e}")

    def obter_tipo_anterior(self, nome_base):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT tipo FROM monitoramento
                WHERE nome = ?
                ORDER BY id DESC
                LIMIT 1
            """, (nome_base,))

            row = cursor.fetchone()

            if row:
                return row[0]

        return self.get_tipo_from_snapshot(nome_base)

    def notificar_evento(self, tipo_operacao, nome, dir_anterior, dir_atual):
        if not self.observador.ativo or self.observador.desligando:
            return

        nome_base = os.path.basename(nome)

        try:
            print(f"Notificando evento: {tipo_operacao} - {nome_base}")
            print(f"  Dir anterior: {dir_anterior}")
            print(f"  Dir atual: {dir_atual}")

            if tipo_operacao == self.observador.loc.get_text("op_deleted"):
                evento = self._criar_evento_exclusao(nome_base, dir_anterior)

                if evento and hasattr(self.observador, 'interface'):
                    from Observador.ob_08_EventoMovido import verificar_movimentacao
                    evento_processado = verificar_movimentacao(self.observador.interface, evento)

                    if evento_processado is None:
                        caminho_completo = os.path.join(dir_anterior, nome_base)

                        arquivo_existe_em_outro_lugar = False
                        if hasattr(self.observador, 'interface') and hasattr(self.observador.interface, 'diretorio_atual'):
                            dir_monitorado = self.observador.interface.diretorio_atual
                            for raiz, dirs, arquivos in os.walk(dir_monitorado):
                                if nome_base in arquivos or nome_base in dirs:
                                    arquivo_existe_em_outro_lugar = True
                                    break

                        if not arquivo_existe_em_outro_lugar and not os.path.exists(caminho_completo):
                            evento["_temporario"] = False
                            self.processar_exclusao(evento)
                            return

                        else:
                            evento["_temporario"] = True
                            self.processar_exclusao(evento)
                            return

                    evento = evento_processado

            else:
                evento = self._criar_evento_padrao(tipo_operacao, nome_base, dir_anterior, dir_atual)

                if evento and hasattr(self.observador, 'interface'):
                    from Observador.ob_08_EventoMovido import verificar_movimentacao
                    evento_processado = verificar_movimentacao(self.observador.interface, evento)

                    if evento_processado and evento_processado["tipo_operacao"] == self.observador.loc.get_text("op_moved"):
                        self._remover_exclusao_temporaria(evento_processado["nome"], evento_processado["dir_anterior"])

                    if evento_processado is None:
                        return
                    
                    evento = evento_processado

            if evento:
                self.registrar_evento_no_banco(evento)

        except Exception as e:
            print(f"Erro ao notificar evento: {e}")
            import traceback
            traceback.print_exc()

    def _remover_exclusao_temporaria(self, nome, dir_anterior):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("BEGIN TRANSACTION")

                cursor.execute("""
                    SELECT id FROM monitoramento 
                    WHERE tipo_operacao = ? AND nome = ? AND dir_anterior = ?
                    ORDER BY id DESC LIMIT 1
                """, (self.observador.loc.get_text("op_deleted"), nome, dir_anterior))

                resultado = cursor.fetchone()
                if resultado:
                    registro_id = resultado[0]

                    cursor.execute("""
                        DELETE FROM monitoramento 
                        WHERE id = ?
                    """, (registro_id,))

                    cursor.execute("""
                        SELECT id FROM excluido 
                        WHERE tipo_operacao = ? AND nome = ? AND dir_anterior = ?
                        ORDER BY id DESC LIMIT 1
                    """, (self.observador.loc.get_text("op_deleted"), nome, dir_anterior))

                    excluido_resultado = cursor.fetchone()
                    if excluido_resultado:
                        excluido_id = excluido_resultado[0]
                        cursor.execute("""
                            DELETE FROM excluido 
                            WHERE id = ?
                        """, (excluido_id,))

                cursor.execute("COMMIT")

        except Exception as e:
            print(f"Erro ao remover exclusão temporária do banco: {e}")
            if 'conn' in locals():
                try:
                    cursor.execute("ROLLBACK")

                except:
                    pass

    def _criar_evento_exclusao(self, nome_base, dir_anterior):
        metadados = self.obter_metadados_arquivo_excluido(nome_base)

        tipo_arquivo = None

        if metadados:
            return {
                "tipo_operacao": self.observador.loc.get_text("op_deleted"),
                "nome": nome_base,
                "dir_anterior": dir_anterior,
                "dir_atual": "",
                "data_criacao": metadados.get("data_criacao", ""),
                "data_modificacao": metadados.get("data_modificacao", ""),
                "data_acesso": metadados.get("data_acesso", ""),
                "tipo": metadados.get("tipo", ""),
                "tamanho": metadados.get("tamanho", ""),
                "atributos": metadados.get("atributos", ""),
                "autor": metadados.get("autor", ""),
                "dimensoes": metadados.get("dimensoes", ""),
                "duracao": metadados.get("duracao", ""),
                "taxa_bits": metadados.get("taxa_bits", ""),
                "protegido": metadados.get("protegido", ""),
                "paginas": metadados.get("paginas", ""),
                "linhas": metadados.get("linhas", ""),
                "palavras": metadados.get("palavras", ""),
                "paginas_estimadas": metadados.get("paginas_estimadas", ""),
                "linhas_codigo": metadados.get("linhas_codigo", ""),
                "total_linhas": metadados.get("total_linhas", ""),
                "slides_estimados": metadados.get("slides_estimados", ""),
                "arquivos": metadados.get("arquivos", ""),
                "descompactados": metadados.get("descompactados", ""),
                "slides": metadados.get("slides", ""),
                "binario": metadados.get("binario", ""),
                "planilhas": metadados.get("planilhas", ""),
                "colunas": metadados.get("colunas", ""),
                "registros": metadados.get("registros", ""),
                "tabelas": metadados.get("tabelas", "")
            }

        if tipo_arquivo is None:
            tipo_arquivo = self.observador.gerenciador_colunas.identificar_tipo_arquivo(nome_base)

        return {
            "tipo_operacao": self.observador.loc.get_text("op_deleted"),
            "nome": nome_base,
            "dir_anterior": dir_anterior,
            "dir_atual": "",
            "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_modificacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_acesso": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo_arquivo,
            "tamanho": "",
            "atributos": "",
            "autor": "",
            "dimensoes": "",
            "duracao": "",
            "taxa_bits": "",
            "protegido": "",
            "paginas": "",
            "linhas": "",
            "palavras": "",
            "paginas_estimadas": "",
            "linhas_codigo": "",
            "total_linhas": "",
            "slides_estimados": "",
            "arquivos": "",
            "descompactados": "",
            "slides": "",
            "binario": "",
            "planilhas": "",
            "colunas": "",
            "registros": "",
            "tabelas": ""
        }

    def _criar_evento_padrao(self, tipo_operacao, nome_base, dir_anterior, dir_atual):
        caminho = dir_atual if os.path.exists(dir_atual) else dir_anterior

        if os.path.exists(caminho):
            e_pasta = self.is_directory(caminho)

            if e_pasta:
                tipo_arquivo = self.observador.loc.get_text("folder")

            else:
                extensao = os.path.splitext(nome_base)[1][1:].lower()
                tipo_arquivo = extensao if extensao else self.observador.loc.get_text("unknown")

            stats = os.stat(caminho)
            data_criacao = datetime.fromtimestamp(stats.st_ctime)
            data_modificacao = datetime.fromtimestamp(stats.st_mtime)
            data_acesso = datetime.fromtimestamp(stats.st_atime)

        else:
            from Observador.GerenciamentoMetadados import identificar_tipo_arquivo

            tipo_arquivo = identificar_tipo_arquivo(nome_base, self.observador.loc)
            if not tipo_arquivo:
                tipo_arquivo = self.get_tipo_from_snapshot(nome_base)

                if not tipo_arquivo:
                    tipo_arquivo = self.observador.loc.get_text("unknown")

            data_criacao = data_modificacao = data_acesso = datetime.now()

        item_data = {
            "nome": nome_base,
            "dir_atual": dir_atual,
            "dir_anterior": dir_anterior,
            "tipo": tipo_arquivo
        }
        metadados = self.observador.gerenciador_colunas.get_metadados(item_data)

        return {
            "tipo_operacao": tipo_operacao,
            "nome": nome_base,
            "dir_anterior": dir_anterior,
            "dir_atual": dir_atual,
            "data_criacao": data_criacao.strftime("%Y-%m-%d %H:%M:%S"),
            "data_modificacao": data_modificacao.strftime("%Y-%m-%d %H:%M:%S"),
            "data_acesso": data_acesso.strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": tipo_arquivo,
            "tamanho": metadados.get("tamanho", ""),
            "atributos": metadados.get("atributos", ""),
            "autor": metadados.get("autor", ""),
            "dimensoes": metadados.get("dimensoes", ""),
            "duracao": metadados.get("duracao", ""),
            "taxa_bits": metadados.get("taxa_bits", ""),
            "protegido": metadados.get("protegido", ""),
            "paginas": metadados.get("paginas", ""),
            "linhas": metadados.get("linhas", ""),
            "palavras": metadados.get("palavras", ""),
            "paginas_estimadas": metadados.get("paginas_estimadas", ""),
            "linhas_codigo": metadados.get("linhas_codigo", ""),
            "total_linhas": metadados.get("total_linhas", ""),
            "slides_estimados": metadados.get("slides_estimados", ""),
            "arquivos": metadados.get("arquivos", ""),
            "descompactados": metadados.get("descompactados", ""),
            "slides": metadados.get("slides", ""),
            "binario": metadados.get("binario", ""),
            "planilhas": metadados.get("planilhas", ""),
            "colunas": metadados.get("colunas", ""),
            "registros": metadados.get("registros", ""),
            "tabelas": metadados.get("tabelas", "")
        }

    def _atualizar_interface_apos_exclusao(self):
        try:
            self.eventos_excluidos += 1

            interface = None
            if self.callback and hasattr(self.callback, '__self__'):
                interface = self.callback.__self__

            elif hasattr(self.observador, 'interface'):
                interface = self.observador.interface

            if interface and hasattr(interface, 'gerenciador_tabela'):
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT MAX(id) FROM monitoramento WHERE tipo_operacao = ?", (self.observador.loc.get_text("op_deleted"),))
                    result = cursor.fetchone()
                    if result and result[0]:
                        ultimo_id_exclusao = result[0]
                        if not hasattr(self, '_ultimo_id_exclusao_exibido'):
                            self._ultimo_id_exclusao_exibido = 0

                        if self._ultimo_id_exclusao_exibido < ultimo_id_exclusao:
                            if ultimo_id_exclusao - self._ultimo_id_exclusao_exibido < 5:
                                for _ in range(ultimo_id_exclusao - self._ultimo_id_exclusao_exibido):
                                    interface.gerenciador_tabela.atualizar_linha_mais_recente(interface.tabela_dados)

                            else:
                                interface.gerenciador_tabela.atualizar_dados_tabela(interface.tabela_dados)

                            self._ultimo_id_exclusao_exibido = ultimo_id_exclusao

                from Observador.ob_08_EventoMovido import _atualizar_contador_eventos
                _atualizar_contador_eventos(interface)

                interface.atualizar_status()

        except Exception as e:
            print(f"Erro ao atualizar interface após exclusão: {e}")

    def processar_eventos_movimentacao(self, eventos_movidos, callback=None):
        if not eventos_movidos:
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA synchronous = OFF")
                cursor.execute("BEGIN TRANSACTION")

                for evento in eventos_movidos:
                    try:
                        self._inserir_evento_movido(cursor, evento)

                    except Exception as e:
                        print(f"Erro ao processar evento movido: {e}")
                        continue

                cursor.execute("COMMIT")
                cursor.execute("PRAGMA synchronous = NORMAL")

                if callback and callable(callback):
                    callback()

        except Exception as e:
            print(f"Erro ao processar lote de eventos movidos: {e}")
            try:
                if 'conn' in locals() and conn:
                    cursor.execute("ROLLBACK")

            except:
                pass

    def _inserir_evento_movido(self, cursor, evento):
        if not evento or evento.get("tipo_operacao") != self.observador.loc.get_text("op_moved"):
            return False

        try:
            colunas = [
                "tipo_operacao", 
                "nome", 
                "dir_anterior", 
                "dir_atual",
                "data_criacao", 
                "data_modificacao", 
                "data_acesso", 
                "tipo", 
                "tamanho",
                "atributos", 
                "autor", 
                "dimensoes", 
                "duracao", 
                "taxa_bits", 
                "protegido",
                "paginas",
                "linhas",
                "palavras",
                "paginas_estimadas",
                "linhas_codigo",
                "total_linhas",
                "slides_estimados",
                "arquivos",
                "descompactados",
                "slides",
                "binario",
                "planilhas",
                "colunas",
                "registros",
                "tabelas", 
                "timestamp"
            ]

            valores = []
            for coluna in colunas:
                if coluna == "tipo_operacao":
                    valores.append(self.observador.loc.get_text("op_moved"))

                elif coluna == "timestamp" and "timestamp" not in evento:
                    valores.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                else:
                    valores.append(evento.get(coluna, ""))

            placeholders = ", ".join(["?" for _ in colunas])
            colunas_str = ", ".join(colunas)

            cursor.execute(f"INSERT INTO movido ({colunas_str}) VALUES ({placeholders})", valores)
            cursor.execute(f"INSERT INTO monitoramento ({colunas_str}) VALUES ({placeholders})", valores)

            return True

        except Exception as e:
            print(f"Erro ao inserir evento movido: {e}")
            return False
