import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import logging
from .gst_01_base_gerador import BaseGerador


class GraficoRadar(BaseGerador):
    __slots__ = []

    def gerar(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("operations_by_file_type") if self.loc else 'Operações por Tipo de Arquivo'

        logger = logging.getLogger('FileManager')
        logger.debug(f"Radar - Dados obtidos: {len(df)} registros")

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        try:
            df_radar = df[['tipo_operacao', 'tipo']].copy()
            df_radar = df_radar.dropna()

            if df_radar.empty:
                return self._criar_grafico_sem_dados(titulo)

            tipos_top = df_radar['tipo'].value_counts().nlargest(6).index.tolist()
            operacoes = df_radar['tipo_operacao'].unique().tolist()

            matriz_radar = np.zeros((len(operacoes), len(tipos_top)))

            for i, operacao in enumerate(operacoes):
                for j, tipo in enumerate(tipos_top):
                    matriz_radar[i, j] = len(df_radar[(df_radar['tipo_operacao'] == operacao) & 
                                                      (df_radar['tipo'] == tipo)])

            for j in range(len(tipos_top)):
                total = matriz_radar[:, j].sum()
                if total > 0:
                    matriz_radar[:, j] = matriz_radar[:, j] / total * 100

            fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': 'polar'})

            angulos = np.linspace(0, 2*np.pi, len(tipos_top), endpoint=False).tolist()
            angulos += angulos[:1]

            tipos_top_show = [t if len(t) < 15 else t[:12] + '...' for t in tipos_top]

            for i, operacao in enumerate(operacoes):
                valores = matriz_radar[i].tolist()
                valores += valores[:1]
                cor = self.cores_operacoes.get(operacao, '#333333')
                ax.plot(angulos, valores, linewidth=2, linestyle='solid', label=operacao, color=cor)
                ax.fill(angulos, valores, alpha=0.1, color=cor)

            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)

            ax.set_xticks(angulos[:-1])
            ax.set_xticklabels(tipos_top_show)

            ax.yaxis.grid(True)
            ax.set_ylim(0, 100)

            plt.title(titulo, y=1.08)
            plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))

            plt.tight_layout()

            return plt.gcf()

        except Exception as e:
            logger.error(f"Radar - Erro ao gerar gráfico de radar: {str(e)}", exc_info=True)
            return self._criar_grafico_sem_dados(f"{titulo} - Erro: {str(e)}")
