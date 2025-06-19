import matplotlib.pyplot as plt
from utils.LogManager import LogManager
from .gst_01_base_gerador import BaseGerador


class GraficoPizza(BaseGerador):
    __slots__ = []

    def gerar(self):
        logger = LogManager.get_logger()
        logger.debug("Iniciando geração do gráfico de pizza")

        try:
            df = self._obter_dados()
            titulo = self.loc.get_text("operations_pie") if self.loc else 'Distribuição de Operações'

            if df.empty:
                logger.warning("Dataset vazio para geração do gráfico de pizza")
                return self._criar_grafico_sem_dados(titulo)

            logger.debug(f"Criando gráfico de pizza com {len(df)} registros")
            plt.figure(figsize=(10, 8))
            contagem = df['tipo_operacao'].value_counts()

            if not contagem.empty:
                cores = [self.cores_operacoes.get(op, '#333333') for op in contagem.index]
                plt.pie(contagem, labels=contagem.index, autopct='%1.1f%%', colors=cores)
                plt.title(titulo)
                logger.debug(f"Gráfico de pizza criado com {len(contagem)} operações diferentes")

            else:
                logger.warning("Nenhuma operação encontrada para gerar o gráfico de pizza")

            return plt.gcf()

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de pizza: {e}", exc_info=True)
            return self._criar_grafico_sem_dados(titulo if 'titulo' in locals() else "Distribuição de Operações")
