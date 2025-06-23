def _criar_mapeamento_funcoes(self, graficos_atualizados):
    mapeamento = {}
    for grafico in graficos_atualizados:
        mapeamento[grafico['func']] = grafico['titulo']

    return mapeamento
