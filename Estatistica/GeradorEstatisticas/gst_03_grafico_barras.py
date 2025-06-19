import matplotlib.pyplot as plt
import seaborn as sns
from utils.LogManager import LogManager
from .gst_01_base_gerador import BaseGerador


class GraficoBarras(BaseGerador):
    __slots__ = []

    def gerar(self):
        logger = LogManager.get_logger()
        logger.debug("Iniciando geração do gráfico de barras")

        try:
            df = self._obter_dados()
            titulo = self.loc.get_text("file_types") if self.loc else 'Top 30 Tipos de Arquivo'

            if df.empty:
                logger.warning("Dataset vazio para geração do gráfico de barras")
                return self._criar_grafico_sem_dados(titulo)

            logger.debug(f"Processando {len(df)} registros para gráfico de barras")
            contagem = df['tipo'].value_counts()[:30]

            if not contagem.empty:
                max_label_len = max([len(str(x)) for x in contagem.index])
                fig_width = max(12, max_label_len * 0.3)
                fig_height = 6 + (len(contagem) > 15) * 2

                logger.debug(f"Criando gráfico de barras com dimensões {fig_width}x{fig_height}")
                fig, ax = plt.subplots(figsize=(fig_width, fig_height))
                sns.barplot(x=contagem.index, y=contagem.values, ax=ax)

                plt.xticks(rotation=90, ha='right')
                ax.set_title(titulo)
                ax.set_xlabel(self.loc.get_text("type") if self.loc else 'Tipo', labelpad=10)
                ax.set_ylabel(self.loc.get_text("quantity") if self.loc else 'Quantidade')

                bottom_margin = min(0.35, max_label_len * 0.015) + 0.1
                plt.subplots_adjust(bottom=bottom_margin)
                fig.tight_layout(pad=1.2, h_pad=None, w_pad=None, rect=[0, 0.05, 1, 0.95])

                logger.debug(f"Gráfico de barras criado com {len(contagem)} tipos de arquivo")

            else:
                logger.warning("Nenhum tipo de arquivo encontrado para gerar o gráfico de barras")

            return plt.gcf()

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de barras: {e}", exc_info=True)
            return self._criar_grafico_sem_dados(titulo if 'titulo' in locals() else "Top 30 Tipos de Arquivo")
