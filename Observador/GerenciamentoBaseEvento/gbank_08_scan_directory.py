def scan_directory(self, directory):
    try:
        from Observador.ob_03_DiretorioScanner import DiretorioScanner
        scanner = DiretorioScanner(self.observador)
        scanner.scan_directory(directory)

    except Exception as e:
        print(f"Erro ao escanear diretório: {e}")
