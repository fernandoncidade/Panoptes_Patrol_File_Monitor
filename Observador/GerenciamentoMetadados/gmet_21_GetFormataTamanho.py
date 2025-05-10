def formata_tamanho(tamanho):
    try:
        if not isinstance(tamanho, (int, float)):
            return "0 B"

        if tamanho < 0:
            return "0 B"

        if tamanho < 1024:
            return f"{tamanho:.0f} B"

        elif tamanho < 1024**2:
            return f"{tamanho/1024:.2f} KB"

        elif tamanho < 1024**3:
            return f"{tamanho/1024**2:.2f} MB"

        elif tamanho < 1024**4:
            return f"{tamanho/1024**3:.2f} GB"

        else:
            return f"{tamanho/1024**4:.2f} TB"

    except Exception as e:
        print(f"Erro ao formatar tamanho: {e}")
        return "0 B"

def get_formata_tamanho(tamanho):
    return formata_tamanho(tamanho)
