import os

def get_file_type(self, caminho):
    if not caminho or not os.path.exists(caminho):
        return self.observador.loc.get_text("unknown")

    if os.path.isdir(caminho):
        return self.observador.loc.get_text("folder")

    ext = os.path.splitext(caminho)[1].lower()

    TIPOS_ARQUIVO = {
        '.pdf': 'pdf',
        '.doc': 'doc',
        '.docx': 'docx',
        '.dotx': 'dotx',
        '.docm': 'docm',
        '.dotm': 'dotm',
        '.xls': 'xls', 
        '.xlsx': 'xlsx',
        '.xlsm': 'xlsm',
        '.xltx': 'xltx',
        '.xltm': 'xltm',
        '.ppt': 'ppt',
        '.pptx': 'pptx',
        '.potx': 'potx',
        '.ppsx': 'ppsx',
        '.mdb': 'mdb',
        '.accdb': 'accdb',
        '.msg': 'msg',
        '.pst': 'pst',
        '.ost': 'ost',
        '.pub': 'pub',
        '.vsd': 'vsd',
        '.vsdx': 'vsdx',
        '.mpp': 'mpp',
        '.mpt': 'mpt',
        '.txt': 'txt',
        '.rtf': 'rtf',
        '.csv': 'csv',
        '.log': 'log',
        '.tmp': 'tmp',
        '.temp': 'temp',
        '.bak': 'bak',
        '.swp': 'swp',
        '.swo': 'swo',
        '.old': 'old',
        '.part': 'part',

        # Imagens
        '.jpg': 'jpg',
        '.jpeg': 'jpeg',
        '.png': 'png',
        '.gif': 'gif',
        '.bmp': 'bmp',
        '.tiff': 'tiff',
        '.tif': 'tif',
        '.webp': 'webp',
        '.svg': 'svg',
        '.psd': 'psd',
        '.raw': 'raw',
        '.heic': 'heic',
        '.heif': 'heif',
        '.cr2': 'cr2',
        '.nef': 'nef',
        '.arw': 'arw',

        # Áudios
        '.mp3': 'mp3',
        '.wav': 'wav',
        '.wma': 'wma',
        '.aac': 'aac',
        '.ogg': 'ogg',
        '.flac': 'flac',
        '.m4a': 'm4a',
        '.aiff': 'aiff',
        '.aif': 'aif',

        # Vídeos
        '.mp4': 'mp4',
        '.avi': 'avi',
        '.mkv': 'mkv',
        '.mov': 'mov',
        '.wmv': 'wmv',
        '.flv': 'flv',
        '.webm': 'webm',
        '.mts': 'mts',
        '.m2ts': 'm2ts',
        '.mpeg': 'mpeg',
        '.m4v': 'm4v',

        # Compactados
        '.zip': 'zip',
        '.rar': 'rar',
        '.7z': '7z',
        '.tar': 'tar',
        '.gz': 'gz',
        '.bz2': 'bz2',
        '.xz': 'xz',
        '.cab': 'cab',

        # Executáveis
        '.exe': 'exe',
        '.msi': 'msi',
        '.bat': 'bat',

        # Código fonte
        '.py': 'py',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'h',
        '.hpp': 'hpp',
        '.cs': 'cs',
        '.js': 'js',
        '.html': 'html',
        '.htm': 'htm',
        '.mht': 'mht',
        '.xhtml': 'xhtml',
        '.mhml': 'mhml',
        '.css': 'css',
        '.php': 'php',
        '.sql': 'sql',
        '.json': 'json',
        '.xml': 'xml',
        '.yaml': 'yaml',
        '.yml': 'yml',
        '.ini': 'ini',
        '.cfg': 'cfg',
        '.conf': 'conf',
        '.log': 'log',
        '.md': 'md',
        '.rst': 'rst',
        '.bat': 'bat',
        '.sh': 'sh',
        '.ps1': 'ps1',
        '.psm1': 'psm1',
        '.psd1': 'psd1',
        '.ps1xml': 'ps1xml',
        '.pssc': 'pssc',
        '.psc1': 'psc1'
    }

    return TIPOS_ARQUIVO.get(ext, ext[1:].upper() if ext else self.observador.loc.get_text("unknown"))
