import os
import win32file
import win32con

def get_atributos_arquivo(item, loc):
    caminho = item.get("dir_atual") or item.get("dir_anterior")

    if not caminho or not os.path.exists(caminho):
        return ""

    try:
        attrs = win32file.GetFileAttributes(caminho)
        atributos = []

        if attrs & win32con.FILE_ATTRIBUTE_READONLY:
            atributos.append(loc.get_text("readonly"))

        if attrs & win32con.FILE_ATTRIBUTE_HIDDEN:
            atributos.append(loc.get_text("hidden"))

        if attrs & win32con.FILE_ATTRIBUTE_SYSTEM:
            atributos.append(loc.get_text("system"))

        if attrs & win32con.FILE_ATTRIBUTE_ARCHIVE:
            atributos.append(loc.get_text("archive"))

        if attrs & win32con.FILE_ATTRIBUTE_ENCRYPTED:
            atributos.append(loc.get_text("encrypted"))

        if attrs & win32con.FILE_ATTRIBUTE_COMPRESSED:
            atributos.append(loc.get_text("compressed"))

        return ", ".join(atributos)

    except Exception:
        if "atributos" in item and item["atributos"]:
            return loc.traduzir_metadados(item["atributos"], "atributos")

        return ""
