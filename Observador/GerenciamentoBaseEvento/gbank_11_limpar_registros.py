import sqlite3

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
