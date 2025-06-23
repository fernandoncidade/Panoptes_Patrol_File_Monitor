from datetime import datetime

def _criar_evento_exclusao(self, nome_base, dir_anterior):
    metadados = self.obter_metadados_arquivo_excluido(nome_base)

    tipo_arquivo = None

    if metadados:
        return {
            "tipo_operacao": self.observador.loc.get_text("op_deleted"),
            "nome": nome_base,
            "dir_anterior": dir_anterior,
            "dir_atual": "",
            "data_criacao": metadados.get("data_criacao", ""),
            "data_modificacao": metadados.get("data_modificacao", ""),
            "data_acesso": metadados.get("data_acesso", ""),
            "tipo": metadados.get("tipo", ""),
            "tamanho": metadados.get("tamanho", ""),
            "atributos": metadados.get("atributos", ""),
            "autor": metadados.get("autor", ""),
            "dimensoes": metadados.get("dimensoes", ""),
            "duracao": metadados.get("duracao", ""),
            "taxa_bits": metadados.get("taxa_bits", ""),
            "protegido": metadados.get("protegido", ""),
            "paginas": metadados.get("paginas", ""),
            "linhas": metadados.get("linhas", ""),
            "palavras": metadados.get("palavras", ""),
            "paginas_estimadas": metadados.get("paginas_estimadas", ""),
            "linhas_codigo": metadados.get("linhas_codigo", ""),
            "total_linhas": metadados.get("total_linhas", ""),
            "slides_estimados": metadados.get("slides_estimados", ""),
            "arquivos": metadados.get("arquivos", ""),
            "descompactados": metadados.get("descompactados", ""),
            "slides": metadados.get("slides", ""),
            "binario": metadados.get("binario", ""),
            "planilhas": metadados.get("planilhas", ""),
            "colunas": metadados.get("colunas", ""),
            "registros": metadados.get("registros", ""),
            "tabelas": metadados.get("tabelas", "")
        }

    if tipo_arquivo is None:
        tipo_arquivo = self.observador.gerenciador_colunas.identificar_tipo_arquivo(nome_base)

    return {
        "tipo_operacao": self.observador.loc.get_text("op_deleted"),
        "nome": nome_base,
        "dir_anterior": dir_anterior,
        "dir_atual": "",
        "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_modificacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_acesso": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo_arquivo,
        "tamanho": "",
        "atributos": "",
        "autor": "",
        "dimensoes": "",
        "duracao": "",
        "taxa_bits": "",
        "protegido": "",
        "paginas": "",
        "linhas": "",
        "palavras": "",
        "paginas_estimadas": "",
        "linhas_codigo": "",
        "total_linhas": "",
        "slides_estimados": "",
        "arquivos": "",
        "descompactados": "",
        "slides": "",
        "binario": "",
        "planilhas": "",
        "colunas": "",
        "registros": "",
        "tabelas": ""
    }
