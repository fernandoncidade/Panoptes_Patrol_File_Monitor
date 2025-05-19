import sqlite3

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
