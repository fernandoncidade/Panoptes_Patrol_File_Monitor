import matplotlib.pyplot as plt
from .gst_01_base_gerador import BaseGerador


class GraficoPizza(BaseGerador):
    __slots__ = []

    def gerar(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("operations_pie") if self.loc else 'Distribuição de Operações'

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        plt.figure(figsize=(10, 8))
        contagem = df['tipo_operacao'].value_counts()

        if not contagem.empty:
            cores = [self.cores_operacoes.get(op, '#333333') for op in contagem.index]
            plt.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=cores)
            plt.title(titulo)

        return plt.gcf()
