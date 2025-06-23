from .gmet_18_GetMetadados import get_metadados

def get_duracao_arquivo( item):
    metadados = get_metadados(item)
    return metadados.get("duracao", "")
