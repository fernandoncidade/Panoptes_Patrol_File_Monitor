import matplotlib.pyplot as plt
import squarify
from utils.LogManager import LogManager
from .gst_01_base_gerador import BaseGerador


class GraficoTreemap(BaseGerador):
    __slots__ = []

    def gerar(self):
        logger = LogManager.get_logger()
        logger.debug("Iniciando geração do gráfico treemap")

        try:
            df = self._obter_dados()
            titulo = self.loc.get_text("tree_map") if self.loc else 'Mapa de Árvore - Tipos de Arquivo'

            if df.empty:
                logger.warning("Dataset vazio para geração do treemap")
                return self._criar_grafico_sem_dados(titulo)

            logger.debug(f"Processando {len(df)} registros para treemap")
            tipos = df['tipo'].value_counts()[:30]

            if not tipos.empty:
                logger.debug(f"Criando treemap com {len(tipos)} tipos de arquivo")
                plt.figure(figsize=(12, 8))
                squarify.plot(sizes=tipos.values, label=tipos.index, alpha=0.6)
                plt.title(titulo)
                plt.axis('off')
                logger.debug("Treemap criado com sucesso")

            else:
                logger.warning("Nenhum tipo de arquivo encontrado para gerar o treemap")

            return plt.gcf()

        except Exception as e:
            logger.error(f"Erro ao gerar treemap: {e}", exc_info=True)
            return self._criar_grafico_sem_dados(titulo if 'titulo' in locals() else "Mapa de Árvore - Tipos de Arquivo")
