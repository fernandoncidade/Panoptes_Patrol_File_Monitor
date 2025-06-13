import matplotlib.pyplot as plt
from .gst_01_base_gerador import BaseGerador


class GraficoPareto(BaseGerador):
    __slots__ = []

    def gerar(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("pareto_analysis") if self.loc else 'Análise de Pareto - Operações'

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        contagem = df['tipo_operacao'].value_counts()
        if not contagem.empty:
            freq_cum = contagem.cumsum() / contagem.sum() * 100

            fig, ax1 = plt.subplots(figsize=(12, 6))
            ax2 = ax1.twinx()

            cores = [self.cores_operacoes.get(op, '#333333') for op in contagem.index]
            ax1.bar(range(len(contagem)), contagem.values, color=cores)
            ax2.plot(range(len(contagem)), freq_cum, 'r-', marker='o')

            ax1.set_xticks(range(len(contagem)))
            ax1.set_xticklabels(contagem.index, rotation=45)

            ax1.set_ylabel(self.loc.get_text("quantity") if self.loc else 'Quantidade')
            ax2.set_ylabel(self.loc.get_text("cumulative_percentage") if self.loc else 'Porcentagem Acumulada')
            plt.title(titulo)

        return plt.gcf()
