import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from .gst_01_base_gerador import BaseGerador


class GraficoHistograma(BaseGerador):
    __slots__ = []

    def gerar(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("hour_histogram") if self.loc else 'Distribuição de Operações por Hora'

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        df['hora'] = pd.to_datetime(df['timestamp']).dt.hour
        plt.figure(figsize=(12, 6))
        sns.histplot(data=df, x='hora', bins=24)
        plt.title(titulo)
        plt.xlabel(self.loc.get_text("hour_of_day") if self.loc else 'Hora do Dia')
        plt.ylabel(self.loc.get_text("quantity") if self.loc else 'Quantidade')

        return plt.gcf()
