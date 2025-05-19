import os
from datetime import datetime

def _criar_evento_padrao(self, tipo_operacao, nome_base, dir_anterior, dir_atual):
    caminho = dir_atual if os.path.exists(dir_atual) else dir_anterior

    if os.path.exists(caminho):
        e_pasta = self.is_directory(caminho)

        if e_pasta:
            tipo_arquivo = self.observador.loc.get_text("folder")

        else:
            extensao = os.path.splitext(nome_base)[1][1:].lower()
            tipo_arquivo = extensao if extensao else self.observador.loc.get_text("unknown")

        stats = os.stat(caminho)
        data_criacao = datetime.fromtimestamp(stats.st_ctime)
        data_modificacao = datetime.fromtimestamp(stats.st_mtime)
        data_acesso = datetime.fromtimestamp(stats.st_atime)

    else:
        from Observador.GerenciamentoMetadados import identificar_tipo_arquivo

        tipo_arquivo = identificar_tipo_arquivo(nome_base, self.observador.loc)
        if not tipo_arquivo:
            tipo_arquivo = self.get_tipo_from_snapshot(nome_base)

            if not tipo_arquivo:
                tipo_arquivo = self.observador.loc.get_text("unknown")

        data_criacao = data_modificacao = data_acesso = datetime.now()

    item_data = {
        "nome": nome_base,
        "dir_atual": dir_atual,
        "dir_anterior": dir_anterior,
        "tipo": tipo_arquivo
    }
    metadados = self.observador.gerenciador_colunas.get_metadados(item_data)

    return {
        "tipo_operacao": tipo_operacao,
        "nome": nome_base,
        "dir_anterior": dir_anterior,
        "dir_atual": dir_atual,
        "data_criacao": data_criacao.strftime("%Y-%m-%d %H:%M:%S"),
        "data_modificacao": data_modificacao.strftime("%Y-%m-%d %H:%M:%S"),
        "data_acesso": data_acesso.strftime("%Y-%m-%d %H:%M:%S"),
        "tipo": tipo_arquivo,
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
