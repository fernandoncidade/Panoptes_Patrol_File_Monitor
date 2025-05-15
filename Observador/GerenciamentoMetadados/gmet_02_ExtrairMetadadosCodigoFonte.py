import os
from datetime import datetime
from .gmet_21_GetFormataTamanho import get_formata_tamanho

def extrair_metadados_codigo_fonte(caminho, loc):
    metadados = {}
    AMOSTRAGEM_LINHAS = 10000

    try:
        if not os.path.exists(caminho):
            return metadados

        stats = os.stat(caminho)
        tamanho = stats.st_size
        encoding = 'utf-8'

        try:
            import chardet

            with open(caminho, 'rb') as f:
                raw_data = f.read(min(tamanho, 100 * 1024))
                detected = chardet.detect(raw_data)

                if detected['confidence'] > 0.7:
                    encoding = detected['encoding']

        except ImportError:
            pass

        total_linhas = 0

        with open(caminho, 'rb') as f:
            total_linhas = sum(1 for _ in f)

        linhas_analisadas = 0
        linhas_codigo = 0
        linhas_comentario = 0
        linhas_vazias = 0
        autores = set()
        estruturas = {'classes': 0, 'funcoes': 0, 'imports': 0}

        is_arquivo_grande = tamanho > 10 * 1024 * 1024

        with open(caminho, 'r', encoding=encoding, errors='ignore') as f:
            for i, linha in enumerate(f):
                if is_arquivo_grande and not (i < AMOSTRAGEM_LINHAS // 2 or i > total_linhas - (AMOSTRAGEM_LINHAS // 2)):
                    continue

                linha = linha.strip()

                if linha.startswith(('class ', 'def ', 'function ', 'import ', 'from ')):
                    if linha.startswith(('import ', 'from ')):
                        estruturas['imports'] += 1

                    elif linha.startswith('class '):
                        estruturas['classes'] += 1

                    elif linha.startswith(('def ', 'function ')):
                        estruturas['funcoes'] += 1

                if not linha:
                    linhas_vazias += 1

                elif linha.startswith(('#', '//', '/*', '*', '--', '%', '"', "'")):
                    linhas_comentario += 1

                    linha_lower = linha.lower()
                    for indicador in ['@author', 'author:', 'created by', 'developed by', 'copyright']:
                        if indicador in linha_lower:
                            autor = linha.split(indicador)[-1].strip(' :*/"\'-')
                            if autor:
                                autores.add(autor)

                else:
                    linhas_codigo += 1

                linhas_analisadas += 1

        if is_arquivo_grande:
            fator = total_linhas / linhas_analisadas if linhas_analisadas > 0 else 1
            linhas_codigo = int(linhas_codigo * fator)
            linhas_comentario = int(linhas_comentario * fator)
            linhas_vazias = int(linhas_vazias * fator)

            for key in estruturas:
                estruturas[key] = int(estruturas[key] * fator)

        metadados.update({
            'total_linhas': total_linhas,
            'linhas_codigo': linhas_codigo,
            'linhas_comentario': linhas_comentario,
            'linhas_vazias': linhas_vazias,
            'porcentagem_comentarios': f"{(linhas_comentario/total_linhas)*100:.1f}%" if total_linhas > 0 else "0%",
            'encoding': encoding,
            'tamanho': get_formata_tamanho(tamanho),
            'data_criacao': datetime.fromtimestamp(stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
            'data_modificacao': datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            'data_acesso': datetime.fromtimestamp(stats.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
            'estruturas': f"Classes: {estruturas['classes']}, Funções: {estruturas['funcoes']}, Imports: {estruturas['imports']}"
        })

        if autores:
            metadados['autor'] = '; '.join(autores)

        return metadados

    except Exception as e:
        print(f"Erro ao extrair metadados do código fonte {caminho}: {e}")
        return metadados
