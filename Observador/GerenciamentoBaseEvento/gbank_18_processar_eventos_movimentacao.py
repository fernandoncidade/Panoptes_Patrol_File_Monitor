import sqlite3

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
