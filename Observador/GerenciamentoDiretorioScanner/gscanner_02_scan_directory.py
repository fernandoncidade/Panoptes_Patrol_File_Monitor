import os
import sqlite3

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
