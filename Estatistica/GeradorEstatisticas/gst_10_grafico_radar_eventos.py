import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from utils.LogManager import LogManager
from .gst_01_base_gerador import BaseGerador


class GraficoRadarEventos(BaseGerador):
    __slots__ = []

    def gerar(self):
        logger = LogManager.get_logger()
        logger.debug("Iniciando geração do gráfico radar de eventos")

        try:
            df = self._obter_dados()
            titulo = self.loc.get_text("events_monitored") if self.loc else 'Eventos Monitorados'

            logger.debug(f"Radar Eventos - Dados obtidos: {len(df)} registros")

            if df.empty:
                logger.warning("Dataset vazio para geração do gráfico radar de eventos")
                return self._criar_grafico_sem_dados(titulo)

            plt.figure(figsize=(14, 10))

            plt.subplot(2, 2, 1, polar=True)
            self._criar_radar_eventos_tipo(df)

            plt.subplot(2, 2, 2, polar=True)
            self._criar_radar_eventos_dia_semana(df)

            plt.subplot(2, 2, 3, polar=True)
            self._criar_radar_eventos_hora(df)

            plt.subplot(2, 2, 4, polar=True)
            self._criar_radar_eventos_operacao(df)

            plt.suptitle(titulo, fontsize=16, fontweight='bold')
            plt.tight_layout()

            logger.debug("Gráfico radar de eventos criado com sucesso")
            return plt.gcf()

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico radar de eventos: {e}", exc_info=True)
            return self._criar_grafico_sem_dados(titulo if 'titulo' in locals() else "Eventos Monitorados")

    def _preparar_dados_temporais(self, df):
        logger = LogManager.get_logger()
        logger.debug("Preparando dados temporais para radar de eventos")

        try:
            if 'timestamp' not in df.columns or df['timestamp'].isna().all():
                logger.warning("Radar Eventos - Sem dados temporais válidos")
                return None

            df_temporal = df.copy()
            df_temporal['timestamp'] = pd.to_datetime(df_temporal['timestamp'], errors='coerce')

            df_temporal = df_temporal.dropna(subset=['timestamp'])

            if df_temporal.empty:
                logger.warning("Radar Eventos - Todos os timestamps são inválidos após conversão")
                return None

            df_temporal['dia_semana'] = df_temporal['timestamp'].dt.dayofweek
            df_temporal['hora'] = df_temporal['timestamp'].dt.hour
            df_temporal['data'] = df_temporal['timestamp'].dt.date

            dias_unicos = df_temporal['data'].nunique()
            logger.debug(f"Radar Eventos - Dados temporais preparados: {len(df_temporal)} registros em {dias_unicos} dias distintos")

            return df_temporal

        except Exception as e:
            logger.error(f"Erro ao preparar dados temporais: {e}", exc_info=True)
            return None

    def _criar_radar_eventos_tipo(self, df):
        logger = LogManager.get_logger()
        logger.debug("Radar Eventos - Criando radar por tipo de arquivo")

        try:
            df_temporal = self._preparar_dados_temporais(df)
            if df_temporal is None:
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados temporais válidos', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("file_types") if self.loc else 'Por Tipo de Arquivo')
                logger.warning("Radar Eventos - Sem dados temporais válidos para radar de tipos")
                return

            eventos_por_tipo = df_temporal['tipo'].value_counts().head(8)
            logger.debug(f"Radar Eventos - Distribuição por tipo: {dict(eventos_por_tipo)}")

            if eventos_por_tipo.empty:
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados suficientes', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("file_types") if self.loc else 'Por Tipo de Arquivo')
                logger.warning("Radar Eventos - Sem tipos de arquivo para plotar")
                return

            categorias = eventos_por_tipo.index.tolist()
            valores = eventos_por_tipo.values.tolist()
            logger.debug(f"Radar Eventos - Usando {len(categorias)} categorias de tipos de arquivo")

            N = len(categorias)

            angulos = [n / float(N) * 2 * np.pi for n in range(N)]
            angulos += angulos[:1]

            valores_radar = valores + [valores[0]]

            ax = plt.gca()
            ax.plot(angulos, valores_radar, 'o-', linewidth=2)
            ax.fill(angulos, valores_radar, alpha=0.25)

            ax.set_xticks(angulos[:-1])
            ax.set_xticklabels(categorias, fontsize=8)

            plt.title(self.loc.get_text("file_types") if self.loc else 'Por Tipo de Arquivo')
            logger.debug("Radar Eventos - Radar por tipo de arquivo criado com sucesso")

        except Exception as e:
            logger.error(f"Radar Eventos - Erro ao criar radar de eventos por tipo: {e}", exc_info=True)
            plt.text(0.5, 0.5, f'Erro: {str(e)}', horizontalalignment='center', 
                    verticalalignment='center', transform=plt.gca().transAxes)
            plt.title(self.loc.get_text("file_types") if self.loc else 'Por Tipo de Arquivo')

    def _criar_radar_eventos_dia_semana(self, df):
        logger = LogManager.get_logger()
        logger.debug("Radar Eventos - Criando radar por dia da semana")

        try:
            df_temporal = self._preparar_dados_temporais(df)
            if df_temporal is None:
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados temporais válidos', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("days") if self.loc else 'Por Dia da Semana')
                logger.warning("Radar Eventos - Sem dados temporais válidos para radar por dia da semana")
                return

            if self.loc:
                dias_semana = [
                    self.loc.get_text("monday"),
                    self.loc.get_text("tuesday"),
                    self.loc.get_text("wednesday"),
                    self.loc.get_text("thursday"),
                    self.loc.get_text("friday"),
                    self.loc.get_text("saturday"),
                    self.loc.get_text("sunday")
                ]

            else:
                dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

            eventos_por_dia = df_temporal['dia_semana'].value_counts().reindex(range(7), fill_value=0).values
            logger.debug(f"Radar Eventos - Distribuição por dia da semana: {dict(zip(dias_semana, eventos_por_dia))}")

            N = 7
            angulos = [n / float(N) * 2 * np.pi for n in range(N)]
            angulos += angulos[:1]

            valores_radar = list(eventos_por_dia) + [eventos_por_dia[0]]
            total_eventos = sum(eventos_por_dia)
            logger.debug(f"Radar Eventos - Total de {total_eventos} eventos distribuídos pelos dias da semana")

            if total_eventos > 0:
                ax = plt.gca()
                ax.plot(angulos, valores_radar, 'o-', linewidth=2, color='green')
                ax.fill(angulos, valores_radar, color='green', alpha=0.25)

                ax.set_xticks(angulos[:-1])
                ax.set_xticklabels(dias_semana, fontsize=8)

                plt.title(self.loc.get_text("days") if self.loc else 'Por Dia da Semana')
                logger.debug("Radar Eventos - Radar por dia da semana criado com sucesso")

            else:
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados suficientes', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("days") if self.loc else 'Por Dia da Semana')
                logger.warning("Radar Eventos - Sem eventos por dia da semana para plotar")

        except Exception as e:
            logger.error(f"Radar Eventos - Erro ao criar radar por dia da semana: {e}", exc_info=True)
            plt.text(0.5, 0.5, f'Erro: {str(e)}', horizontalalignment='center', 
                    verticalalignment='center', transform=plt.gca().transAxes)
            plt.title(self.loc.get_text("days") if self.loc else 'Por Dia da Semana')

    def _criar_radar_eventos_hora(self, df):
        logger = LogManager.get_logger()
        logger.debug("Radar Eventos - Criando radar por hora")

        try:
            df_temporal = self._preparar_dados_temporais(df)
            if df_temporal is None:
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados temporais válidos', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("hour_of_day") if self.loc else 'Por Hora do Dia')
                logger.warning("Radar Eventos - Sem dados temporais válidos para radar por hora")
                return

            eventos_por_hora = df_temporal['hora'].value_counts().reindex(range(24), fill_value=0)

            distribuicao_completa = dict(eventos_por_hora)
            logger.debug(f"Radar Eventos - Distribuição completa por hora: {distribuicao_completa}")

            horas_mostradas = list(range(0, 24, 2))
            eventos_hora_filtrado = eventos_por_hora[horas_mostradas]
            categorias = [f"{h}h" for h in horas_mostradas]
            valores = eventos_hora_filtrado.values.tolist()

            total_eventos = sum(valores)
            logger.debug(f"Radar Eventos - Total de {total_eventos} eventos nas horas selecionadas")

            N = len(categorias)

            if total_eventos > 0:
                angulos = [n / float(N) * 2 * np.pi for n in range(N)]
                angulos += angulos[:1]

                valores_radar = valores + [valores[0]]

                ax = plt.gca()
                ax.plot(angulos, valores_radar, 'o-', linewidth=2, color='purple')
                ax.fill(angulos, valores_radar, color='purple', alpha=0.25)

                ax.set_xticks(angulos[:-1])
                ax.set_xticklabels(categorias, fontsize=8)

                plt.title(self.loc.get_text("hour_of_day") if self.loc else 'Por Hora do Dia')
                logger.debug("Radar Eventos - Radar por hora do dia criado com sucesso")

            else:
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados temporais suficientes', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("hour_of_day") if self.loc else 'Por Hora do Dia')
                logger.warning("Radar Eventos - Sem eventos por hora para plotar")

        except Exception as e:
            logger.error(f"Radar Eventos - Erro ao criar radar por hora: {e}", exc_info=True)
            plt.text(0.5, 0.5, f'Erro: {str(e)}', horizontalalignment='center', 
                    verticalalignment='center', transform=plt.gca().transAxes)
            plt.title(self.loc.get_text("hour_of_day") if self.loc else 'Por Hora do Dia')

    def _criar_radar_eventos_operacao(self, df):
        logger = LogManager.get_logger()
        logger.debug("Radar Eventos - Criando radar por operação")

        try:
            df_temporal = self._preparar_dados_temporais(df)
            if df_temporal is None or 'tipo_operacao' not in df_temporal.columns:
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Dados de operação não disponíveis', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("operation_type") if self.loc else 'Por Tipo de Operação')
                logger.warning(f"Radar Eventos - {'Dados temporais inválidos' if df_temporal is None else 'Coluna tipo_operacao não encontrada'}")
                return

            eventos_por_operacao = df_temporal['tipo_operacao'].value_counts()
            logger.debug(f"Radar Eventos - Distribuição por operação: {dict(eventos_por_operacao)}")

            if eventos_por_operacao.empty:
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados suficientes', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("operation_type") if self.loc else 'Por Tipo de Operação')
                logger.warning("Radar Eventos - Sem operações para plotar")
                return

            categorias = eventos_por_operacao.index.tolist()
            valores = eventos_por_operacao.values.tolist()
            logger.debug(f"Radar Eventos - Usando {len(categorias)} categorias de operações")

            cores = [self.cores_operacoes.get(cat, '#333333') for cat in categorias]

            N = len(categorias)
            angulos = [n / float(N) * 2 * np.pi for n in range(N)]
            angulos += angulos[:1]

            valores_radar = valores + [valores[0]]

            ax = plt.gca()
            ax.plot(angulos, valores_radar, 'o-', linewidth=2)
            ax.fill(angulos, valores_radar, alpha=0.25)

            ax.set_xticks(angulos[:-1])
            ax.set_xticklabels(categorias, fontsize=8)

            plt.title(self.loc.get_text("operation_type") if self.loc else 'Por Tipo de Operação')
            logger.debug("Radar Eventos - Radar por operação criado com sucesso")

        except Exception as e:
            logger.error(f"Radar Eventos - Erro ao criar radar por operação: {e}", exc_info=True)
            plt.text(0.5, 0.5, f'Erro: {str(e)}', horizontalalignment='center', 
                    verticalalignment='center', transform=plt.gca().transAxes)
            plt.title(self.loc.get_text("operation_type") if self.loc else 'Por Tipo de Operação')
