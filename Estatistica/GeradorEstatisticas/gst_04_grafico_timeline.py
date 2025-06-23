import matplotlib.pyplot as plt
import pandas as pd
from utils.LogManager import LogManager
from .gst_01_base_gerador import BaseGerador


class GraficoTimeline(BaseGerador):
    __slots__ = []

    def gerar(self):
        logger = LogManager.get_logger()
        logger.debug("Iniciando geração do gráfico de timeline")

        try:
            df = self._obter_dados()
            titulo = self.loc.get_text("timeline") if self.loc else 'Timeline de Operações'

            if df.empty:
                logger.warning("Dataset vazio para geração do gráfico de timeline")
                return self._criar_grafico_sem_dados(titulo)

            logger.debug(f"Processando {len(df)} registros para timeline")
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            plt.figure(figsize=(12, 6))

            operacoes = df['tipo_operacao'].unique()
            logger.debug(f"Encontradas {len(operacoes)} operações distintas para timeline")

            if len(operacoes) > 0:
                for op in operacoes:
                    op_data = df[df['tipo_operacao'] == op]
                    if not op_data.empty:
                        plt.scatter(op_data['timestamp'], 
                                [op] * len(op_data), 
                                label=op, 
                                alpha=0.6,
                                color=self.cores_operacoes.get(op, '#333333'))

                        logger.debug(f"Adicionado {len(op_data)} pontos para operação '{op}'")

                plt.legend()

            else:
                logger.warning("Nenhuma operação encontrada para gerar a timeline")

            plt.title(titulo)
            plt.xlabel(self.loc.get_text("date_time") if self.loc else 'Data/Hora')
            plt.ylabel(self.loc.get_text("operation_type") if self.loc else 'Tipo de Operação')

            logger.debug("Gráfico de timeline criado com sucesso")
            return plt.gcf()

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de timeline: {e}", exc_info=True)
            return self._criar_grafico_sem_dados(titulo if 'titulo' in locals() else "Timeline de Operações")
