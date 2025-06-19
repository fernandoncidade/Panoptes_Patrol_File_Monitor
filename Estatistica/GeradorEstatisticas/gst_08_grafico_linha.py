import matplotlib.pyplot as plt
import pandas as pd
from utils.LogManager import LogManager
from .gst_01_base_gerador import BaseGerador


class GraficoLinha(BaseGerador):
    __slots__ = []

    def gerar(self):
        logger = LogManager.get_logger()
        logger.debug("Iniciando geração do gráfico de linha")

        try:
            df = self._obter_dados()
            titulo = self.loc.get_text("operations_by_day") if self.loc else 'Operações por Dia'

            if df.empty:
                logger.warning("Dataset vazio para geração do gráfico de linha")
                return self._criar_grafico_sem_dados(titulo)

            logger.debug(f"Processando {len(df)} registros para gráfico de linha por dia")
            df['data'] = pd.to_datetime(df['timestamp']).dt.date
            ops_por_dia = pd.crosstab(df['data'], df['tipo_operacao'])

            if not ops_por_dia.empty:
                total_por_dia = ops_por_dia.sum(axis=1)
                logger.debug(f"Criando gráfico de linha para {len(ops_por_dia)} dias distintos")

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

                resumo = {
                    'dias': len(ops_por_dia),
                    'operacoes': list(ops_por_dia.columns),
                    'media_diaria': float(total_por_dia.mean()),
                    'total': int(total_por_dia.sum())
                }
                logger.debug(f"Resumo do gráfico de linha: {resumo}")

            else:
                logger.warning("Nenhum dado por dia encontrado para gerar o gráfico de linha")

            return plt.gcf()

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de linha: {e}", exc_info=True)
            return self._criar_grafico_sem_dados(titulo if 'titulo' in locals() else "Operações por Dia")
