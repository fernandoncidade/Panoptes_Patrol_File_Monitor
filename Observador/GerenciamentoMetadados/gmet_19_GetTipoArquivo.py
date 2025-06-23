import os

def identificar_tipo_arquivo(caminho, loc):
    nome_arquivo = os.path.basename(caminho).lower()
    ext = os.path.splitext(caminho)[1].lower()

    if ext.lower() == '.tmp':
        return "tmp"

    if nome_arquivo.startswith(("~", "._", ".#", "~$")) or \
       nome_arquivo.endswith(("~", ".lock")) or \
       "temp-index" in nome_arquivo or \
       "~index" in nome_arquivo:
        return loc.get_text("file_temp")

    TIPOS_TEMPORARIOS = {'.tmp', '.temp', '.~', '.swp', '.swo', '.$$', '.old', '.part', 
                         '.cache', '.crdownload', '.download', '.partial', '.lock', '.thumb'}

    TIPOS_IMAGEM = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.psd', '.svg',
                    '.webp', '.raw', '.heic', '.heif', '.cr2', '.nef', '.arw'}

    TIPOS_AUDIO = {'.wav', '.mp3', '.aac', '.flac', '.ogg', '.aiff', '.wma', '.m4a', '.aif'}

    TIPOS_VIDEO = {'.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.webm', '.mts', '.m2ts', '.mpeg', '.m4v'}

    TIPOS_CODIGO_FONTE = {'.py','.java', '.cpp', '.c', '.h', '.hpp','.cs', '.js', '.html',
                          '.htm', '.mht', '.xhtml', '.mhml', '.css', '.php', '.sql', '.json',
                          '.xml', '.yaml', '.yml', '.md', '.rst',
                          '.bat', '.sh', '.ps1', '.psm1', '.psd1', '.ps1xml', '.pssc', '.psc1'}

    TIPOS_DOCUMENTO = {'.doc', '.docx', '.pdf', '.rtf', '.txt', '.odt', '.wpd', '.pages'}

    TIPOS_PLANILHA = {'.xls', '.xlsx', '.xlsm', '.ods', '.csv', '.tsv', '.numbers'}

    TIPOS_APRESENTACAO = {'.ppt', '.pptx', '.odp', '.key'}

    TIPOS_BANCO_DADOS = {'.dat', '.db', '.sqlite', '.mdb', '.accdb', '.sav', '.spss', '.db-journal'}

    TIPOS_EXECUTAVEIS = {'.exe', '.dll', '.bin', '.app', '.apk', '.msi', '.run', '.bat', '.cmd'}

    TIPOS_COMPACTADOS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.cab'}

    TIPOS_BACKUP = {'.bak', '.bkp', '.backup', '.old', '.orig', '.save', '.sav', '.auto'}

    TIPOS_LOG = {'.log', '.trace', '.dmp', '.dump', '.hprof', '.core', '.err', '.out'}

    TIPOS_CONFIGURACAO = {'.ini', '.cfg', '.config', '.conf', '.properties', '.plist', '.toml', '.settings'}

    if ext in TIPOS_IMAGEM:
        return loc.get_text("file_image")

    elif ext in TIPOS_AUDIO:
        return loc.get_text("file_audio")

    elif ext in TIPOS_VIDEO:
        return loc.get_text("file_video")

    elif ext in TIPOS_CODIGO_FONTE:
        return loc.get_text("file_source_code")

    elif ext in TIPOS_DOCUMENTO:
        return loc.get_text("file_document")

    elif ext in TIPOS_PLANILHA:
        return loc.get_text("file_spreadsheet")

    elif ext in TIPOS_APRESENTACAO:
        return loc.get_text("file_presentation")

    elif ext in TIPOS_BANCO_DADOS:
        return loc.get_text("file_database")

    elif ext in TIPOS_EXECUTAVEIS:
        return loc.get_text("file_executable")
    
    elif ext in TIPOS_TEMPORARIOS:
        return loc.get_text("file_temp")

    elif ext in TIPOS_COMPACTADOS:
        return loc.get_text("file_archive")

    elif ext in TIPOS_BACKUP:
        return loc.get_text("file_backup")

    elif ext in TIPOS_LOG:
        return loc.get_text("file_log")

    elif ext in TIPOS_CONFIGURACAO:
        return loc.get_text("file_config")

    elif ext:
        return f"{ext[1:].lower()}"

    return loc.get_text("unknown")
