import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from utils.LogManager import LogManager
from .gst_01_base_gerador import BaseGerador


class GraficoHeatmap(BaseGerador):
    __slots__ = []

    def gerar(self):
        logger = LogManager.get_logger()
        logger.debug("Iniciando geração do gráfico heatmap")

        df = self._obter_dados()
        titulo = self.loc.get_text("temporal_distribution") if self.loc else 'Distribuição Temporal'

        logger.debug(f"Heatmap - Dados obtidos: {len(df)} registros")

        if df.empty:
            logger.warning("Dataset vazio para geração do heatmap")
            return self._criar_grafico_sem_dados(titulo)

        try:
            df_temporal, escala_info = self._preparar_dados_temporais(df)
            if df_temporal is None:
                logger.warning("Não foi possível preparar dados temporais para o heatmap")
                return self._criar_grafico_sem_dados(titulo)

            logger.debug(f"Heatmap - Dados temporais preparados com escala: {escala_info['escala']}")
            plt.figure(figsize=(12, 8))

            matriz_heatmap = self._criar_matriz_heatmap(df_temporal)
            logger.debug(f"Heatmap - Matriz criada com dimensões {matriz_heatmap.shape}")

            dias_semana = self._obter_nomes_dias_semana()
            logger.debug(f"Heatmap - Usando {len(dias_semana)} dias da semana")

            ax = plt.gca()
            im = ax.imshow(matriz_heatmap, cmap='YlOrRd', aspect='auto')

            ax.set_yticks(np.arange(len(dias_semana)))
            ax.set_yticklabels(dias_semana)
            ax.set_xticks(np.arange(0, 24, 2))
            ax.set_xticklabels(np.arange(0, 24, 2))

            cbar = plt.colorbar(im)
            cbar.set_label(self.loc.get_text("quantity") if self.loc else 'Quantidade')

            plt.xlabel(escala_info['xlabel'])
            plt.ylabel(self.loc.get_text("days_of_week") if self.loc else 'Dias da Semana')
            plt.title(f"{titulo} ({escala_info['escala_nome']})")

            plt.tight_layout()
            logger.debug("Heatmap gerado com sucesso")

            return plt.gcf()

        except Exception as e:
            logger.error(f"Heatmap - Erro ao gerar mapa de calor: {e}", exc_info=True)
            return self._criar_grafico_sem_dados(titulo)

    def _preparar_dados_temporais(self, df):
        logger = LogManager.get_logger()
        logger.debug("Heatmap - Preparando dados temporais")

        if 'timestamp' not in df.columns or df['timestamp'].isna().all():
            logger.warning("Heatmap - Sem dados temporais válidos")
            return None, None

        try:
            df_temporal = df.copy()
            df_temporal['timestamp'] = pd.to_datetime(df_temporal['timestamp'], errors='coerce')

            validos_antes = len(df)
            df_temporal = df_temporal.dropna(subset=['timestamp'])
            validos_depois = len(df_temporal)
            logger.debug(f"Heatmap - Conversão de timestamps: {validos_antes} registros → {validos_depois} válidos ({validos_antes - validos_depois} removidos)")

            if df_temporal.empty:
                logger.warning("Heatmap - Todos os timestamps são inválidos após conversão")
                return None, None

            df_temporal, escala_info = self._ajustar_escala_temporal(df_temporal)

            return df_temporal, escala_info

        except Exception as e:
            logger.error(f"Heatmap - Erro ao preparar dados temporais: {e}", exc_info=True)
            return None, None

    def _ajustar_escala_temporal(self, df):
        logger = LogManager.get_logger()

        try:
            if len(df) <= 1:
                logger.debug("Heatmap - Dados insuficientes, usando escala de hora")
                df['dia_semana'] = df['timestamp'].dt.dayofweek
                df['hora'] = df['timestamp'].dt.hour
                return df, {
                    'escala': 'hora',
                    'escala_nome': self.loc.get_text("hour_of_day") if self.loc else 'Hora do Dia',
                    'xlabel': self.loc.get_text("hour_of_day") if self.loc else 'Hora do Dia'
                }

            data_min = df['timestamp'].min()
            data_max = df['timestamp'].max()
            intervalo_total = data_max - data_min

            logger.debug(f"Heatmap - Intervalo total: {intervalo_total} (de {data_min} até {data_max})")

            total_segundos = intervalo_total.total_seconds()
            total_minutos = total_segundos / 60
            total_horas = total_minutos / 60
            total_dias = total_horas / 24

            escala_info = {}

            if total_segundos < 1:
                logger.debug("Heatmap - Escala: milissegundos")
                df['dia_semana'] = 0
                df['hora'] = ((df['timestamp'] - data_min).dt.total_seconds() * 1000).astype(int) % 24
                escala_info = {
                    'escala': 'milissegundos',
                    'escala_nome': self.loc.get_text("ms") if self.loc else 'ms',
                    'xlabel': self.loc.get_text("time_milliseconds") if self.loc else 'Tempo (milissegundos)'
                }

            elif total_segundos < 10:
                logger.debug("Heatmap - Escala: centisegundos")
                df['dia_semana'] = 0
                df['hora'] = ((df['timestamp'] - data_min).dt.total_seconds() * 100).astype(int) % 24
                escala_info = {
                    'escala': 'centisegundos',
                    'escala_nome': self.loc.get_text("time_centiseconds") if self.loc else 'Centésimos',
                    'xlabel': self.loc.get_text("time_centiseconds") if self.loc else 'Tempo (centésimos de segundo)'
                }

            elif total_segundos < 60:
                logger.debug("Heatmap - Escala: segundos")
                df['dia_semana'] = 0
                df['hora'] = (df['timestamp'] - data_min).dt.total_seconds().astype(int) % 24
                escala_info = {
                    'escala': 'segundos',
                    'escala_nome': self.loc.get_text("time_seconds") if self.loc else 'Segundos',
                    'xlabel': self.loc.get_text("time_seconds") if self.loc else 'Tempo (segundos)'
                }

            elif total_minutos < 60:
                logger.debug("Heatmap - Escala: minutos")
                df['dia_semana'] = 0
                df['hora'] = ((df['timestamp'] - data_min).dt.total_seconds() / 60).astype(int) % 24
                escala_info = {
                    'escala': 'minutos',
                    'escala_nome': self.loc.get_text("time_minutes") if self.loc else 'Minutos',
                    'xlabel': self.loc.get_text("time_minutes") if self.loc else 'Tempo (minutos)'
                }

            elif total_horas < 24:
                logger.debug("Heatmap - Escala: horas")
                df['dia_semana'] = 0
                df['hora'] = df['timestamp'].dt.hour
                escala_info = {
                    'escala': 'horas',
                    'escala_nome': self.loc.get_text("time_hours") if self.loc else 'Horas',
                    'xlabel': self.loc.get_text("hour_of_day") if self.loc else 'Hora do Dia'
                }

            else:
                logger.debug("Heatmap - Escala: dia_hora (padrão)")
                df['dia_semana'] = df['timestamp'].dt.dayofweek
                df['hora'] = df['timestamp'].dt.hour
                escala_info = {
                    'escala': 'dia_hora',
                    'escala_nome': self.loc.get_text("days_of_week") if self.loc else 'Dias da Semana',
                    'xlabel': self.loc.get_text("hour_of_day") if self.loc else 'Hora do Dia'
                }

            logger.debug(f"Heatmap - Escala selecionada: {escala_info['escala']} com {df['dia_semana'].nunique()} dias distintos e {df['hora'].nunique()} horas distintas")
            return df, escala_info

        except Exception as e:
            logger.error(f"Heatmap - Erro ao ajustar escala temporal: {e}", exc_info=True)

            try:
                df['dia_semana'] = df['timestamp'].dt.dayofweek
                df['hora'] = df['timestamp'].dt.hour

            except:
                df['dia_semana'] = 0
                df['hora'] = 0

            return df, {
                'escala': 'erro',
                'escala_nome': 'Erro',
                'xlabel': 'Erro na escala'
            }

    def _criar_matriz_heatmap(self, df):
        logger = LogManager.get_logger()
        logger.debug("Heatmap - Criando matriz para heatmap")

        try:
            dias_unicos = sorted(df['dia_semana'].unique())
            horas_unicas = sorted(df['hora'].unique())
            logger.debug(f"Heatmap - Dias únicos: {dias_unicos}, Horas únicas: {horas_unicas}")

            contagem = df.groupby(['dia_semana', 'hora']).size().unstack(fill_value=0)
            logger.debug(f"Heatmap - Matriz de contagem criada com formato: {contagem.shape}")

            matriz_completa = pd.DataFrame(index=range(7), columns=range(24), data=0)

            if not contagem.empty:
                for dia in contagem.index:
                    for hora in contagem.columns:
                        matriz_completa.at[dia, hora] = contagem.at[dia, hora]

                total_eventos = matriz_completa.values.sum()
                logger.debug(f"Heatmap - Total de {total_eventos} eventos na matriz")

                max_valor = matriz_completa.values.max()
                min_valor = matriz_completa.values.min() if total_eventos > 0 else 0
                logger.debug(f"Heatmap - Valores da matriz: min={min_valor}, max={max_valor}")

            return matriz_completa.values

        except Exception as e:
            logger.error(f"Heatmap - Erro ao criar matriz heatmap: {e}", exc_info=True)
            return np.zeros((7, 24))

    def _obter_nomes_dias_semana(self):
        logger = LogManager.get_logger()

        try:
            if self.loc:
                dias_semana = [
                    self.loc.get_text("monday") if self.loc.get_text("monday") else "Segunda",
                    self.loc.get_text("tuesday") if self.loc.get_text("tuesday") else "Terça",
                    self.loc.get_text("wednesday") if self.loc.get_text("wednesday") else "Quarta",
                    self.loc.get_text("thursday") if self.loc.get_text("thursday") else "Quinta",
                    self.loc.get_text("friday") if self.loc.get_text("friday") else "Sexta",
                    self.loc.get_text("saturday") if self.loc.get_text("saturday") else "Sábado",
                    self.loc.get_text("sunday") if self.loc.get_text("sunday") else "Domingo"
                ]

                logger.debug("Heatmap - Usando nomes de dias da semana traduzidos")

            else:
                dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
                logger.debug("Heatmap - Usando nomes de dias da semana padrão")

            return dias_semana

        except Exception as e:
            logger.error(f"Heatmap - Erro ao obter nomes dos dias da semana: {e}", exc_info=True)
            return ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab', 'Dom']
