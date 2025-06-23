import os

def extrair_metadados_config(caminho, loc):
    metadados = {}
    nome_arquivo = os.path.basename(caminho).lower()
    ext = os.path.splitext(caminho)[1].lower()

    try:
        formatos_config = {
            ".ini": "Formato INI",
            ".conf": "Arquivo de Configuração",
            ".cfg": "Arquivo de Configuração",
            ".config": "Arquivo de Configuração XML",
            ".json": "Configuração JSON",
            ".yaml": "Configuração YAML",
            ".yml": "Configuração YAML",
            ".properties": "Arquivo de Propriedades Java",
            ".xml": "Configuração XML",
            ".plist": "Property List (macOS/iOS)",
            ".reg": "Registro do Windows",
            ".toml": "Tom's Obvious, Minimal Language",
            ".settings": "Configuração do Visual Studio",
        }

        if ext in formatos_config:
            metadados['formato'] = formatos_config[ext]

        elif "config" in nome_arquivo:
            metadados['formato'] = "Arquivo de Configuração"

        elif "settings" in nome_arquivo:
            metadados['formato'] = "Arquivo de Configurações"

        else:
            metadados['formato'] = "Configuração desconhecida"

        aplicacoes_conhecidas = {
            "nginx": "Servidor Web Nginx",
            "apache": "Servidor Web Apache",
            "httpd": "Servidor Web Apache",
            "php": "PHP",
            "mysql": "MySQL",
            "postgres": "PostgreSQL",
            "docker": "Docker",
            "kubernetes": "Kubernetes",
            "java": "Java",
            ".net": ".NET",
            "python": "Python",
            "npm": "Node.js/NPM",
            "webpack": "Webpack",
            "vscode": "Visual Studio Code",
            "git": "Git",
            "ssh": "SSH",
            "windows": "Windows",
            "linux": "Linux",
            "log4j": "Log4j",
            "tomcat": "Tomcat",
            "maven": "Maven",
            "gradle": "Gradle",
            "aws": "Amazon Web Services",
            "azure": "Microsoft Azure",
            "google": "Google Cloud",
            "firebase": "Firebase"
        }

        with open(caminho, 'r', encoding='utf-8', errors='ignore') as f:
            conteudo = f.read(8192)

            for app, descricao in aplicacoes_conhecidas.items():
                if app in nome_arquivo.lower() or app in conteudo.lower():
                    metadados['aplicacao'] = descricao
                    break

            linhas = conteudo.splitlines()
            linhas_nao_vazias = [l for l in linhas if l.strip()]

            if ext == '.json':
                try:
                    import json
                    dados = json.loads(conteudo)
                    keys_nivel1 = list(dados.keys())
                    metadados['secoes'] = ", ".join(keys_nivel1[:5])
                    if len(keys_nivel1) > 5:
                        metadados['secoes'] += f" {loc.get_text("and_others")} {len(keys_nivel1)-5}"

                except:
                    pass

            elif ext in ['.yaml', '.yml']:
                secoes = []
                for linha in linhas:
                    if linha.strip() and not linha.startswith(' ') and ':' in linha:
                        secao = linha.split(':')[0].strip()
                        secoes.append(secao)

                if secoes:
                    metadados['secoes'] = ", ".join(secoes[:5])
                    if len(secoes) > 5:
                        metadados['secoes'] += f" {loc.get_text("and_others")} {len(secoes)-5}"

            elif ext in ['.ini', '.conf', '.cfg']:
                secoes = []
                for linha in linhas:
                    if linha.strip().startswith('[') and linha.strip().endswith(']'):
                        secao = linha.strip()[1:-1]
                        secoes.append(secao)

                if secoes:
                    metadados['secoes'] = ", ".join(secoes[:5])
                    if len(secoes) > 5:
                        metadados['secoes'] += f" {loc.get_text("and_others")} {len(secoes)-5}"

            metadados['linhas'] = len(linhas_nao_vazias)

            props = 0
            for linha in linhas_nao_vazias:
                linha = linha.strip()
                if '=' in linha or ':' in linha and not linha.startswith(('#', '//', ';', '[')):
                    props += 1

            metadados['propriedades'] = props

    except Exception as e:
        print(f"Erro ao extrair metadados da configuração {caminho}: {e}")

    return metadados
