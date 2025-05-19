def _atualizar_progresso(self):
    if hasattr(self.observador, 'interface'):
        progresso = (self.contador_processados / self.total_arquivos) * 100 if self.total_arquivos > 0 else 0
        if abs(progresso - self.ultimo_progresso) >= 1:
            self.ultimo_progresso = progresso
            self.progresso_atualizado.emit(int(progresso), self.contador_processados, self.total_arquivos)
