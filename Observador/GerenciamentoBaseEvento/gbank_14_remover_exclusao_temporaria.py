import sqlite3

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
