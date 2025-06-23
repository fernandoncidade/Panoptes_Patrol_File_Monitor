def traduzir_tipo_operacao(localizador, valor, idioma_origem=None):
    operacoes_normalizadas = {
        "op_renamed": ["op_renamed", "renamed", "renomeado", "renombrado", "renommé", "rinominato", "umbenannt"],
        "op_added": ["op_added", "added", "adicionado", "añadido", "ajouté", "aggiunto", "hinzugefügt"],
        "op_deleted": ["op_deleted", "deleted", "excluído", "eliminado", "supprimé", "eliminato", "gelöscht"],
        "op_modified": ["op_modified", "modified", "modificado", "modificado", "modifié", "modificato", "geändert"],
        "op_moved": ["op_moved", "moved", "movido", "movido", "déplacé", "spostato", "verschoben"],
        "op_scanned": ["op_scanned", "scanned", "escaneado", "escanneado", "numérisé", "scansionato", "gescannt"]
    }

    operacao_normalizada = None
    for chave, variantes in operacoes_normalizadas.items():
        if valor in variantes or valor.lower() in variantes:
            operacao_normalizada = chave
            break

    if operacao_normalizada is None:
        for chave, variantes in operacoes_normalizadas.items():
            for variante in variantes:
                if valor and variante and variante.lower() in valor.lower():
                    operacao_normalizada = chave
                    break

            if operacao_normalizada:
                break

    if operacao_normalizada is None:
        return valor

    return localizador.get_text(operacao_normalizada)

def traduzir_metadados(localizador, valor, campo):
    if not valor or not isinstance(valor, str):
        return valor

    if campo == "tipo":
        tipo_mapeamento = {
            # Português
            "pasta": "folder",
            "vídeo": "file_video",
            "imagem": "file_image",
            "audio": "file_audio",
            "código fonte": "file_source_code",
            "documento": "file_document",
            "planilha": "file_spreadsheet",
            "apresentação": "file_presentation",
            "banco de dados": "file_database",
            "executável": "file_executable",
            "temporário": "file_temp",
            "compactado": "file_archive",
            "backup": "file_backup",
            "registro": "file_log",
            "configuração": "file_config",
            "desconhecido": "unknown",

            # English
            "folder": "folder",
            "video": "file_video",
            "image": "file_image",
            "audio": "file_audio",
            "source code": "file_source_code",
            "document": "file_document",
            "spreadsheet": "file_spreadsheet",
            "presentation": "file_presentation",
            "database": "file_database",
            "executable": "file_executable",
            "temporary": "file_temp",
            "archive": "file_archive",
            "backup": "file_backup",
            "registry": "file_log",
            "config": "file_config",
            "unknown": "unknown",

            # Español
            "carpeta": "folder",
            "video": "file_video",
            "imagen": "file_image",
            "audio": "file_audio",
            "código fuente": "file_source_code",
            "documento": "file_document",
            "hoja de cálculo": "file_spreadsheet",
            "presentación": "file_presentation",
            "base de datos": "file_database",
            "ejecutable": "file_executable",
            "temporal": "file_temp",
            "comprimido": "file_archive",
            "respaldo": "file_backup",
            "registro": "file_log",
            "configuración": "file_config",
            "desconocido": "unknown",

            # Français
            "dossier": "folder",
            "vidéo": "file_video",
            "image": "file_image",
            "audio": "file_audio",
            "code source": "file_source_code",
            "document": "file_document",
            "tableur": "file_spreadsheet",
            "présentation": "file_presentation",
            "base de données": "file_database",
            "exécutable": "file_executable",
            "temporaire": "file_temp",
            "compressé": "file_archive",
            "sauvegarde": "file_backup",
            "registre": "file_log",
            "configuration": "file_config",
            "inconnu": "unknown",

            # Italiano
            "cartella": "folder",
            "video": "file_video",
            "immagine": "file_image",
            "audio": "file_audio",
            "codice sorgente": "file_source_code",
            "documento": "file_document",
            "foglio di calcolo": "file_spreadsheet",
            "presentazione": "file_presentation",
            "database": "file_database",
            "eseguibile": "file_executable",
            "temporaneo": "file_temp",
            "compresso": "file_archive",
            "backup": "file_backup",
            "registro": "file_log",
            "configurazione": "file_config",
            "sconosciuto": "unknown",

            # Alemão
            "ordner": "folder",
            "video": "file_video",
            "bild": "file_image",
            "audio": "file_audio",
            "quellcode": "file_source_code",
            "dokument": "file_document",
            "tabellenkalkulation": "file_spreadsheet",
            "präsentation": "file_presentation",
            "datenbank": "file_database",
            "ausführbar": "file_executable",
            "vorübergehend": "file_temp",
            "komprimiert": "file_archive",
            "sicherung": "file_backup",
            "protokoll": "file_log",
            "konfiguration": "file_config",
            "unbekannt": "unknown"
        }

        valor_lower = valor.lower()
        for texto, chave in tipo_mapeamento.items():
            if texto in valor_lower:
                return localizador.get_text(chave)

    elif campo == "atributos":
        atributos_mapeamento = {
            # Português
            "somente leitura": "readonly",
            "oculto": "hidden",
            "sistema": "system",
            "arquivo": "archive",
            "criptografado": "encrypted",
            "compactado": "compressed",

            # English
            "read only": "readonly",
            "hidden": "hidden",
            "system": "system",
            "archive": "archive",
            "encrypted": "encrypted",
            "compressed": "compressed",

            # Español
            "solo lectura": "readonly",
            "oculto": "hidden",
            "sistema": "system",
            "archivo": "archive",
            "cifrado": "encrypted",
            "comprimido": "compressed",

            # Français
            "lecture seule": "readonly",
            "caché": "hidden",
            "système": "system",
            "archive": "archive",
            "chiffré": "encrypted",
            "compressé": "compressed",

            # Italiano
            "sola lettura": "readonly",
            "nascosto": "hidden",
            "sistema": "system",
            "archivio": "archive",
            "cifrato": "encrypted",
            "compresso": "compressed",

            # Alemão
            "schreibgeschützt": "readonly",
            "versteckt": "hidden",
            "system": "system",
            "archiv": "archive",
            "verschlüsselt": "encrypted",
            "komprimiert": "compressed"
        }

        partes_traduzidas = []
        partes = valor.split(", ")

        for parte in partes:
            parte_traduzida = parte
            parte_lower = parte.lower()

            for texto, chave in atributos_mapeamento.items():
                if texto == parte_lower:
                    parte_traduzida = localizador.get_text(chave)
                    break

            partes_traduzidas.append(parte_traduzida)

        return ", ".join(partes_traduzidas)

    elif campo == "autor":
        autor_mapeamento = {
            # Português
            "autor desconhecido": "unknown_author",
            "autor desconhecido - excel": "xls",
            "autor desconhecido - access": "access",
            "autor desconhecido - outlook": "outllok",
            "autor desconhecido - publisher": "publisher", 
            "autor desconhecido - visio": "visio",
            "autor desconhecido - project": "project",
            "autor desconhecido - arquivo comprimido": "compressed_file",

            # English
            "unknown author": "unknown_author",
            "unknown author - excel": "xls",
            "unknown author - access": "access",
            "unknown author - outlook": "outllok",
            "unknown author - publisher": "publisher",
            "unknown author - visio": "visio",
            "unknown author - project": "project",
            "unknown author - compressed file": "compressed_file",

            # Español
            "autor desconocido": "unknown_author",
            "autor desconocido - excel": "xls",
            "autor desconocido - access": "access",
            "autor desconocido - outlook": "outllok",
            "autor desconocido - publisher": "publisher",
            "autor desconocido - visio": "visio",
            "autor desconocido - project": "project",
            "autor desconocido - archivo comprimido": "compressed_file",

            # Français
            "auteur inconnu": "unknown_author",
            "auteur inconnu - excel": "xls",
            "auteur inconnu - access": "access",
            "auteur inconnu - outlook": "outllok",
            "auteur inconnu - publisher": "publisher",
            "auteur inconnu - visio": "visio",
            "auteur inconnu - project": "project",
            "auteur inconnu - fichier compressé": "compressed_file",

            # Italiano
            "autore sconosciuto": "unknown_author",
            "autore sconosciuto - excel": "xls",
            "autore sconosciuto - access": "access",
            "autore sconosciuto - outlook": "outllok",
            "autore sconosciuto - publisher": "publisher",
            "autore sconosciuto - visio": "visio",
            "autore sconosciuto - project": "project",
            "autore sconosciuto - file compresso": "compressed_file",

            # Alemão
            "unbekannter autor": "unknown_author",
            "unbekannter autor - excel": "xls",
            "unbekannter autor - access": "access",
            "unbekannter autor - outlook": "outllok",
            "unbekannter autor - publisher": "publisher",
            "unbekannter autor - visio": "visio",
            "unbekannter autor - project": "project",
            "unbekannter autor - komprimierte datei": "compressed_file"
        }

        valor_lower = valor.lower()
        for texto, chave in autor_mapeamento.items():
            if texto == valor_lower:
                return localizador.get_text(chave)

    elif campo == "protegido":
        if valor.lower() in ["sim", "yes", "sí", "oui", "ja"]:
            return localizador.get_text("yes")

        elif valor.lower() in ["não", "no", "non", "nein"]:
            return localizador.get_text("no")

        for prefix in ["sim", "yes", "sí", "oui", "ja"]:
            if valor.lower().startswith(prefix + " ("):
                complemento = valor[len(prefix)+1:]
                return f"{localizador.get_text('yes')} {complemento}"

        for prefix in ["sim", "yes", "sí", "oui", "ja"]:
            if valor.lower().startswith(prefix + ", "):
                resto = valor[len(prefix)+2:]

                resto_traduzido = traduzir_metadados(localizador, resto, "atributos")

                return f"{localizador.get_text('yes')}, {resto_traduzido}"

    elif campo in ["dimensoes", "tamanho"]:
        binary_patterns = ["binário:", "binary:", "binario:", "fichier binaire:", "binario:", "binär:"]
        for pattern in binary_patterns:
            if pattern in valor.lower():
                parts = valor.split(":", 1)
                if len(parts) == 2:
                    return f"{localizador.get_text('binary_file')}: {parts[1].strip()}"

        unidades_mapeamento = {
            # Português
            "páginas": "pages",
            "páginas estimadas": "pages_estimated",
            "págs.": "pages",
            "págs. est.": "pages_estimated",
            "linhas": "lines",
            "linhas de código": "lines_code",
            "total de linhas": "total_lines",
            "palavras": "words",
            "colunas": "columns",
            "planilhas": "spreadsheets",
            "slides": "slides",
            "slides estimados": "slides_estimated",
            "descompactado": "unzipped",
            "e outros": "and_others",
            "arquivos": "files",
            "tabelas": "tables",
            "parágrafos": "paragraphs",
            "configurações": "settings",
            "registros": "records",
            "registros estimados": "records_estimated",
            "bytes por registro": "bytes_per_record",
            "bytes": "bytes",
            "binário": "binary_file",
            "minutos": "minutes",
            "horas": "hours",
            "dias": "days",
            "tamanho": "size",

            # English
            "pages": "pages",
            "estimated pages": "pages_estimated",
            "est. pages": "pages_estimated",
            "lines": "lines",
            "lines of code": "lines_code",
            "total lines": "total_lines",
            "words": "words",
            "columns": "columns",
            "spreadsheets": "spreadsheets",
            "slides": "slides",
            "estimated slides": "slides_estimated",
            "unzipped": "unzipped",
            "and others": "and_others",
            "files": "files",
            "tables": "tables",
            "paragraphs": "paragraphs",
            "settings": "settings",
            "records": "records",
            "estimated records": "records_estimated",
            "bytes per record": "bytes_per_record",
            "bytes": "bytes",
            "binary": "binary_file",
            "minutes": "minutes",
            "hours": "hours",
            "days": "days",
            "size": "size",

            # Español
            "páginas": "pages",
            "páginas estimadas": "pages_estimated",
            "líneas": "lines",
            "líneas de código": "lines_code",
            "total de líneas": "total_lines",
            "palabras": "words",
            "columnas": "columns",
            "hojas de cálculo": "spreadsheets",
            "diapositivas": "slides",
            "diapositivas estimadas": "slides_estimated",
            "descomprimido": "unzipped",
            "y otros": "and_others",
            "archivos": "files",
            "tablas": "tables",
            "párrafos": "paragraphs",
            "configuraciones": "settings",
            "registros": "records",
            "registros estimados": "records_estimated",
            "bytes por registro": "bytes_per_record",
            "bytes": "bytes",
            "binario": "binary_file",
            "minutos": "minutes",
            "horas": "hours",
            "días": "days",
            "tamaño": "size",

            # Français
            "pages": "pages",
            "pages estimées": "pages_estimated",
            "lignes": "lines",
            "lignes de code": "lines_code",
            "total des lignes": "total_lines",
            "mots": "words",
            "colonnes": "columns",
            "feuilles de calcul": "spreadsheets",
            "diapositives": "slides",
            "diapositives estimées": "slides_estimated",
            "décompressé": "unzipped",
            "et autres": "and_others",
            "fichiers": "files",
            "tables": "tables",
            "paragraphes": "paragraphs",
            "paramètres": "settings",
            "enregistrements": "records",
            "enregistrements estimés": "records_estimated",
            "octets par enregistrement": "bytes_per_record",
            "octets": "bytes",
            "fichier binaire": "binary_file",
            "minutes": "minutes",
            "heures": "hours",
            "jours": "days",
            "taille": "size",

            # Italiano
            "pagine": "pages",
            "pagine stimate": "pages_estimated",
            "righe": "lines",
            "righe di codice": "lines_code",
            "totale righe": "total_lines",
            "parole": "words",
            "colonne": "columns",
            "fogli di calcolo": "spreadsheets",
            "diapositive": "slides",
            "diapositive stimate": "slides_estimated",
            "decompresso": "unzipped",
            "e altri": "and_others",
            "file": "files",
            "tabelle": "tables",
            "paragrafi": "paragraphs",
            "impostazioni": "settings",
            "record": "records",
            "record stimati": "records_estimated",
            "byte per record": "bytes_per_record",
            "byte": "bytes",
            "binario": "binary_file",
            "minuti": "minutes",
            "ore": "hours",
            "giorni": "days",
            "dimensioni": "size",

            # Alemão
            "seiten": "pages",
            "geschätzte seiten": "pages_estimated",
            "zeilen": "lines",
            "codezeilen": "lines_code",
            "gesamtzeilen": "total_lines",
            "wörter": "words",
            "spalten": "columns",
            "tabellenkalkulationen": "spreadsheets",
            "folien": "slides",
            "geschätzte folien": "slides_estimated",
            "entpackt": "unzipped",
            "und andere": "and_others",
            "dateien": "files",
            "tabellen": "tables",
            "absätze": "paragraphs",
            "einstellungen": "settings",
            "datensätze": "records",
            "geschätzte datensätze": "records_estimated",
            "bytes pro datensatz": "bytes_per_record",
            "bytes": "bytes",
            "binär": "binary_file",
            "minuten": "minutes",
            "stunden": "hours",
            "tage": "days",
            "größe": "size"
        }

        import re
        arquivo_compactado_pattern = r'(\d+)\s+(files|arquivos|archivos|fichiers|file|dateien),\s+(.*?)\s+(unzipped|descompactados|descomprimidos|décompressés|decompressi|entpackt)'
        match = re.search(arquivo_compactado_pattern, valor, re.IGNORECASE)

        if match:
            num_arquivos = match.group(1)
            tamanho = match.group(3)
            return f"{num_arquivos} {localizador.get_text('files')}, {tamanho} {localizador.get_text('unzipped')}"

        pattern = r'(\d+|~\d+)\s+([a-zA-ZáàâäãåçéèêëíìîïñóòôöõúùûüýÿæœÁÀÂÄÃÅÇÉÈÊËÍÌÎÏÑÓÒÔÖÕÚÙÛÜÝŸÆŒ\s.]+?)(?=,|\s+\d|\s*$)'
        matches = re.findall(pattern, valor)

        if matches:
            partes_traduzidas = []
            texto_restante = valor

            for numero, unidade in matches:
                unidade_trim = unidade.strip()
                unidade_traduzida = unidade_trim

                for texto, chave in unidades_mapeamento.items():
                    if texto.lower() == unidade_trim.lower():
                        unidade_traduzida = localizador.get_text(chave)
                        break

                padrao_substituicao = f"{numero} {unidade_trim}"
                substituicao = f"{numero} {unidade_traduzida}"
                texto_restante = texto_restante.replace(padrao_substituicao, substituicao)

            return texto_restante

    return valor
