import sqlite3

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
