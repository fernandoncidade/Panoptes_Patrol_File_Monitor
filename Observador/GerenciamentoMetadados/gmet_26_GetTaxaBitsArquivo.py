from .gmet_18_GetMetadados import get_metadados

def get_taxa_bits_arquivo(item):
    metadados = get_metadados(item)
    return metadados.get("taxa_bits", "")
