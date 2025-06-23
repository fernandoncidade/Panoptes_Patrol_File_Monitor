import sqlite3

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
