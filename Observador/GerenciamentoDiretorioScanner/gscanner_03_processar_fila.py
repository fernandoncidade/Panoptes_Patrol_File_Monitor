import queue

def _processar_fila(self):
    while True:
        try:
            item, caminho, tipo = self.fila_processamento.get(timeout=1)
            self._processar_item(item, caminho, tipo)
            self.fila_processamento.task_done()
            self.contador_processados += 1

        except queue.Empty:
            break

        except Exception as e:
            print(f"Erro no processamento: {e}")
            self.fila_processamento.task_done()
