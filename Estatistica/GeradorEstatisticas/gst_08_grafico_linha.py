import matplotlib.pyplot as plt
import pandas as pd
from .gst_01_base_gerador import BaseGerador


class GraficoLinha(BaseGerador):
    __slots__ = []
    
    def gerar(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("operations_by_day") if self.loc else 'Operações por Dia'

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        df['data'] = pd.to_datetime(df['timestamp']).dt.date
        ops_por_dia = pd.crosstab(df['data'], df['tipo_operacao'])

        if not ops_por_dia.empty:
            total_por_dia = ops_por_dia.sum(axis=1)

            fig, ax1 = plt.subplots(figsize=(12, 6))
            ax2 = ax1.twinx()

            cores = {col: self.cores_operacoes.get(col, '#333333') for col in ops_por_dia.columns}
            ops_por_dia.plot(kind='bar', ax=ax1, width=0.8, color=cores, legend=False)

            ax2.plot(range(len(total_por_dia)), total_por_dia, 'r-', linewidth=2)

            ax1.set_title(titulo)
            ax1.set_xlabel(self.loc.get_text("date") if self.loc else 'Data')
            ax1.set_ylabel(self.loc.get_text("quantity_by_type") if self.loc else 'Quantidade por Tipo')
            ax2.set_ylabel(self.loc.get_text("total_operations") if self.loc else 'Total de Operações')

            handles, labels = ax1.get_legend_handles_labels()
            if handles and labels:
                ax1.legend(handles, labels)

            plt.xticks(rotation=45)
            plt.tight_layout()

        return plt.gcf()
