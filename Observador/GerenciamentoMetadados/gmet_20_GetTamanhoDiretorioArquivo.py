import os
from .gmet_21_GetFormataTamanho import get_formata_tamanho

def get_tamanho_diretorio_arquivo(self, item_data, loc):
    try:
        caminho = item_data.get("dir_atual") or item_data.get("dir_anterior", "")
        if not caminho or not os.path.exists(caminho):
            return ""

        with self.lock_cache:
            if caminho in self.cache_metadados and "tamanho" in self.cache_metadados[caminho]:
                return self.cache_metadados[caminho]["tamanho"]

        if os.path.isfile(caminho):
            try:
                tamanho = os.path.getsize(caminho)
                resultado = get_formata_tamanho(tamanho)

                with self.lock_cache:
                    if caminho not in self.cache_metadados:
                        self.cache_metadados[caminho] = {}

                    self.cache_metadados[caminho]["tamanho"] = resultado

                return resultado

            except Exception as e:
                print(f"Erro ao obter tamanho do arquivo {caminho}: {e}")
                return ""

        total_bytes = 0
        arquivos_ignorados = 0

        try:
            def calcular_tamanho_dir(dir_path):
                nonlocal total_bytes, arquivos_ignorados

                try:
                    with os.scandir(dir_path) as entries:
                        for entry in entries:
                            try:
                                if entry.is_file(follow_symlinks=False):
                                    total_bytes += entry.stat().st_size

                                elif entry.is_dir(follow_symlinks=False):
                                    calcular_tamanho_dir(entry.path)

                            except (OSError, IOError, PermissionError) as e:
                                print(f"Erro ao processar {entry.path}: {e}")
                                arquivos_ignorados += 1

                except Exception as e:
                    print(f"Erro ao escanear diretório {dir_path}: {e}")
                    arquivos_ignorados += 1

            calcular_tamanho_dir(caminho)

            resultado = get_formata_tamanho(total_bytes)
            if arquivos_ignorados > 0:
                resultado = f"{resultado} ({arquivos_ignorados} {loc.get_text("ignored")})"

            with self.lock_cache:
                if caminho not in self.cache_metadados:
                    self.cache_metadados[caminho] = {}

                self.cache_metadados[caminho]["tamanho"] = resultado

            return resultado

        except Exception as e:
            print(f"Erro ao calcular tamanho do diretório {caminho}: {e}")
            return ""

    except Exception as e:
        print(f"Erro geral no cálculo de tamanho: {e}")
        return ""
