import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from utils.LogManager import LogManager
from .gst_01_base_gerador import BaseGerador


class GraficoHistograma(BaseGerador):
    __slots__ = []

    def gerar(self):
        logger = LogManager.get_logger()
        logger.debug("Iniciando geração do histograma")

        try:
            df = self._obter_dados()
            titulo = self.loc.get_text("hour_histogram") if self.loc else 'Distribuição de Operações por Hora'

            if df.empty:
                logger.warning("Dataset vazio para geração do histograma")
                return self._criar_grafico_sem_dados(titulo)

            logger.debug(f"Processando {len(df)} registros para histograma de horas")
            df['hora'] = pd.to_datetime(df['timestamp']).dt.hour

            horas_contagem = df['hora'].value_counts().sort_index()
            logger.debug(f"Distribuição de horas: {dict(horas_contagem)}")

            plt.figure(figsize=(12, 6))
            sns.histplot(data=df, x='hora', bins=24)
            plt.title(titulo)
            plt.xlabel(self.loc.get_text("hour_of_day") if self.loc else 'Hora do Dia')
            plt.ylabel(self.loc.get_text("quantity") if self.loc else 'Quantidade')

            logger.debug("Histograma por hora criado com sucesso")
            return plt.gcf()

        except Exception as e:
            logger.error(f"Erro ao gerar histograma: {e}", exc_info=True)
            return self._criar_grafico_sem_dados(titulo if 'titulo' in locals() else "Distribuição de Operações por Hora")
