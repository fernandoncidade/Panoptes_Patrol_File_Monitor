import matplotlib.pyplot as plt
import pandas as pd
from .gst_01_base_gerador import BaseGerador


class GraficoTimeline(BaseGerador):
    __slots__ = []
    
    def gerar(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("timeline") if self.loc else 'Timeline de Operações'

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        df['timestamp'] = pd.to_datetime(df['timestamp'])
        plt.figure(figsize=(12, 6))

        operacoes = df['tipo_operacao'].unique()
        if len(operacoes) > 0:
            for op in operacoes:
                op_data = df[df['tipo_operacao'] == op]
                if not op_data.empty:
                    plt.scatter(op_data['timestamp'], 
                            [op] * len(op_data), 
                            label=op, 
                            alpha=0.6,
                            color=self.cores_operacoes.get(op, '#333333'))

            plt.legend()

        plt.title(titulo)
        plt.xlabel(self.loc.get_text("date_time") if self.loc else 'Data/Hora')
        plt.ylabel(self.loc.get_text("operation_type") if self.loc else 'Tipo de Operação')

        return plt.gcf()
