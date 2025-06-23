import os
import sys
import subprocess
from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _abrir_diretorio(self, caminho):
    try:
        if sys.platform == 'win32':
            os.startfile(caminho)

        elif sys.platform == 'darwin':
            subprocess.call(['open', caminho])

        else:
            subprocess.call(['xdg-open', caminho])

    except Exception as e:
        logger.error(f"Erro ao abrir diretório: {e}", exc_info=True)
