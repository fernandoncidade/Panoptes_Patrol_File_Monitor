def run(self):
    try:
        self.scanner.scan_directory(self.directory)
        self.finished.emit()

    except Exception as e:
        self.error.emit(str(e))
