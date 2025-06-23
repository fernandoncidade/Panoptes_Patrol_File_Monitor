import os
import re

def extrair_metadados_log(caminho, loc):
    metadados = {}

    try:
        tamanho = os.path.getsize(caminho)

        primeiras_linhas = []
        ultimas_linhas = []

        with open(caminho, 'rb') as f:
            contador = 0
            for linha_bin in f:
                if contador >= 10:
                    break

                try:
                    linha = linha_bin.decode('utf-8', errors='ignore').strip()
                    if linha:
                        primeiras_linhas.append(linha)
                        contador += 1

                except:
                    pass

                if f.tell() > 100000: 
                    break

        if tamanho > 10000:
            try:
                with open(caminho, 'rb') as f:
                    pos_final = max(0, tamanho - 4096)
                    f.seek(pos_final)
                    dados_finais = f.read()

                    texto_final = dados_finais.decode('utf-8', errors='ignore')
                    linhas_finais = texto_final.splitlines()
                    ultimas_linhas = linhas_finais[-10:] if len(linhas_finais) > 10 else linhas_finais

            except Exception as e:
                print(f"Erro ao ler últimas linhas: {e}")
                ultimas_linhas = []

        padroes_data = [
            r'(\d{4}[-/]\d{2}[-/]\d{2})',  # YYYY-MM-DD
            r'(\d{2}[-/]\d{2}[-/]\d{4})',  # DD-MM-YYYY
            r'(\d{2}[-/]\d{2}[-/]\d{2})',  # DD-MM-YY
            r'(\d{2}:\d{2}:\d{2})',        # HH:MM:SS
            r'(\d{4}[-/]\d{2}[-/]\d{2}\s+\d{2}:\d{2}:\d{2})'  # YYYY-MM-DD HH:MM:SS
        ]

        datas_encontradas = []
        for linha in primeiras_linhas + ultimas_linhas:
            for padrao in padroes_data:
                matches = re.findall(padrao, linha)
                if matches:
                    datas_encontradas.extend(matches)

        if datas_encontradas:
            primeira_data = datas_encontradas[0]
            ultima_data = datas_encontradas[-1]
            metadados['periodo_log'] = f"{primeira_data} a {ultima_data}"

        linhas = 0
        with open(caminho, 'rb') as f:
            for _ in f:
                linhas += 1

        metadados['linhas'] = f"{linhas:,}".replace(',', '.')

        tipos_log = {
            "apache": ["apache", "httpd", "access.log", "error.log"],
            "nginx": ["nginx", "access.log", "error.log"],
            "sistema": ["syslog", "system.log", "messages", "kern.log", "dmesg"],
            "aplicação": ["app.log", "application.log", "debug.log"],
            "banco de dados": ["mysql", "postgresql", "oracle", "sql", "query"],
            "erro": ["error", "exception", "crash", "fail", "fault"],
            "segurança": ["security", "auth", "firewall", "iptables"],
            "debug": ["debug", "trace", "verbose"],
            "eventos": ["event", "activity"]
        }

        nome_arquivo = os.path.basename(caminho).lower()

        for tipo, palavras_chave in tipos_log.items():
            for palavra in palavras_chave:
                if palavra in nome_arquivo or any(palavra in linha.lower() for linha in primeiras_linhas[:3]):
                    metadados['tipo_log'] = f"{loc.get_text('log_of')} {tipo}"
                    break

            else:
                continue

            break
        else:
            metadados['tipo_log'] = "Log genérico"

        niveis_log = ["error", "warning", "info", "debug", "critical", "fatal", "trace", "notice", "alert"]
        niveis_encontrados = set()

        for linha in primeiras_linhas + ultimas_linhas:
            linha_lower = linha.lower()
            for nivel in niveis_log:
                if nivel in linha_lower:
                    niveis_encontrados.add(nivel)

        if niveis_encontrados:
            metadados['niveis_log'] = ", ".join(niveis_encontrados)

    except Exception as e:
        print(f"Erro ao extrair metadados do log {caminho}: {e}")

    return metadados
