import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import logging
import re
from datetime import datetime, timedelta
from .gst_01_base_gerador import BaseGerador


class GraficoScatter(BaseGerador):
    __slots__ = []

    def _parse_tamanho(self, tamanho_str):
        if pd.isna(tamanho_str) or tamanho_str == '':
            return None

        tamanho_str = str(tamanho_str).strip().lower()

        pattern = r'(\d+(?:[.,]\d+)?)\s*([a-z]*)'
        match = re.match(pattern, tamanho_str)

        if not match:
            return None

        numero_str = match.group(1).replace(',', '.')
        unidade = match.group(2)

        try:
            numero = float(numero_str)
        except ValueError:
            return None

        multiplicadores = {
            'b': 1,
            'kb': 1024,
            'mb': 1024**2,
            'gb': 1024**3,
            'tb': 1024**4
        }

        multiplicador = multiplicadores.get(unidade, 1)
        return int(numero * multiplicador)

    def _ajustar_escala_temporal(self, df_plot):
        if len(df_plot) <= 1:
            return df_plot, self.loc.get_text("date_time") if self.loc else "Data/Hora", None

        data_min = df_plot['timestamp'].min()
        data_max = df_plot['timestamp'].max()
        intervalo_total = data_max - data_min

        logger = logging.getLogger('FileManager')
        logger.debug(f"Scatter - Intervalo total: {intervalo_total}")

        total_segundos = intervalo_total.total_seconds()
        total_minutos = total_segundos / 60
        total_horas = total_minutos / 60
        total_dias = total_horas / 24

        df_ajustado = df_plot.copy()

        if total_segundos < 60:
            if total_segundos < 1:
                inicio = data_min
                df_ajustado['x_plot'] = [(ts - inicio).total_seconds() * 1000 for ts in df_plot['timestamp']]
                xlabel = self.loc.get_text("time_milliseconds") if self.loc else "Tempo (milissegundos)"
                formato_tick = lambda x, pos: f"{x:.0f}{self.loc.get_text('ms') if self.loc else 'ms'}"

            else:
                inicio = data_min
                df_ajustado['x_plot'] = [(ts - inicio).total_seconds() * 100 for ts in df_plot['timestamp']]
                xlabel = self.loc.get_text("time_centiseconds") if self.loc else "Tempo (centésimos de segundo)"
                formato_tick = lambda x, pos: f"{x/100:.2f}{self.loc.get_text('s') if self.loc else 's'}"

        elif total_minutos < 60:
            inicio = data_min
            df_ajustado['x_plot'] = [(ts - inicio).total_seconds() for ts in df_plot['timestamp']]
            xlabel = self.loc.get_text("time_seconds") if self.loc else "Tempo (segundos)"
            formato_tick = lambda x, pos: f"{x:.0f}{self.loc.get_text('s') if self.loc else 's'}"

        elif total_horas < 24:
            inicio = data_min
            df_ajustado['x_plot'] = [(ts - inicio).total_seconds() / 60 for ts in df_plot['timestamp']]
            xlabel = self.loc.get_text("time_minutes") if self.loc else "Tempo (minutos)"
            formato_tick = lambda x, pos: f"{x:.0f}{self.loc.get_text('min') if self.loc else 'min'}"

        elif total_dias < 7:
            inicio = data_min
            df_ajustado['x_plot'] = [(ts - inicio).total_seconds() / 3600 for ts in df_plot['timestamp']]
            xlabel = self.loc.get_text("time_hours") if self.loc else "Tempo (horas)"
            formato_tick = lambda x, pos: f"{x:.1f}{self.loc.get_text('h') if self.loc else 'h'}"

        elif total_dias < 30:
            inicio = data_min
            df_ajustado['x_plot'] = [(ts - inicio).days + (ts - inicio).seconds / 86400 for ts in df_plot['timestamp']]
            xlabel = self.loc.get_text("time_days") if self.loc else "Tempo (dias)"
            formato_tick = lambda x, pos: f"{x:.1f}{self.loc.get_text('d') if self.loc else 'd'}"

        else:
            df_ajustado['x_plot'] = df_plot['timestamp']
            xlabel = self.loc.get_text("date_time") if self.loc else "Data/Hora"
            formato_tick = None

        logger.debug(f"Scatter - Escala selecionada: {xlabel}")
        return df_ajustado, xlabel, formato_tick

    def _configurar_eixo_x(self, df_ajustado, xlabel, formato_tick):
        if formato_tick is not None:
            plt.xlabel(xlabel)
            ax = plt.gca()
            ax.xaxis.set_major_formatter(plt.FuncFormatter(formato_tick))

            if len(df_ajustado) > 0:
                x_min = df_ajustado['x_plot'].min()
                x_max = df_ajustado['x_plot'].max()

                margem = (x_max - x_min) * 0.05
                plt.xlim(x_min - margem, x_max + margem)

                intervalo = x_max - x_min
                if intervalo > 0:
                    if intervalo < 10:
                        step = max(1, intervalo / 10)

                    elif intervalo < 100:
                        step = max(5, intervalo / 10)

                    else:
                        step = max(10, intervalo / 10)

                    ticks = np.arange(x_min, x_max + step, step)
                    plt.xticks(ticks)
        else:
            plt.xlabel(xlabel)
            if len(df_ajustado) > 1:
                data_min = df_ajustado['timestamp'].min()
                data_max = df_ajustado['timestamp'].max()
                margem = timedelta(days=(data_max - data_min).days * 0.05 + 1)
                plt.xlim(data_min - margem, data_max + margem)

    def gerar(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("file_size_analysis") if self.loc else 'Análise de Tamanho de Arquivo'

        logger = logging.getLogger('FileManager')
        logger.debug(f"Scatter - Dados obtidos: {len(df)} registros")

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        try:
            df['tamanho_bytes'] = df['tamanho'].apply(self._parse_tamanho)
            df_filtrado = df.dropna(subset=['tamanho_bytes'])

            df_filtrado = df_filtrado[df_filtrado['tamanho_bytes'] > 0]

            logger.debug(f"Scatter - Registros após filtragem: {len(df_filtrado)}")

            if len(df_filtrado) == 0:
                return self._criar_grafico_sem_dados(self.loc.get_text("no_size_data") if self.loc else "Sem dados de tamanho disponíveis")

            df_filtrado['timestamp'] = pd.to_datetime(df_filtrado['timestamp'], errors='coerce')
            df_filtrado = df_filtrado.dropna(subset=['timestamp'])

            df_filtrado['tamanho_mb'] = df_filtrado['tamanho_bytes'] / (1024 * 1024)

            limite_superior = df_filtrado['tamanho_mb'].quantile(0.99)
            df_plot = df_filtrado[df_filtrado['tamanho_mb'] <= limite_superior]

            logger.debug(f"Scatter - Registros para plotagem: {len(df_plot)}")
            logger.debug(f"Scatter - Tamanhos (MB): min={df_plot['tamanho_mb'].min():.2f}, max={df_plot['tamanho_mb'].max():.2f}")

            df_ajustado, xlabel, formato_tick = self._ajustar_escala_temporal(df_plot)

            plt.figure(figsize=(12, 8))

            cores = [self.cores_operacoes.get(op, '#333333') for op in df_ajustado['tipo_operacao']]

            if formato_tick is not None:
                x_values = df_ajustado['x_plot']
            else:
                x_values = df_ajustado['timestamp']

            scatter = plt.scatter(
                x_values, 
                df_ajustado['tamanho_mb'],
                c=cores,
                alpha=0.6, 
                edgecolors='none',
                s=50
            )

            tipos_operacao = df_ajustado['tipo_operacao'].unique()
            handles = []
            labels = []

            for tipo in tipos_operacao:
                color = self.cores_operacoes.get(tipo, '#333333')
                handles.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10))
                labels.append(tipo)

            plt.legend(handles, labels, loc='upper left')

            self._configurar_eixo_x(df_ajustado, xlabel, formato_tick)
            plt.ylabel(self.loc.get_text("file_size_mb") if self.loc else 'Tamanho do Arquivo (MB)')
            plt.title(titulo)

            if df_ajustado['tamanho_mb'].max() / (df_ajustado['tamanho_mb'].min() + 0.001) > 100:
                plt.yscale('log')

            plt.grid(True, alpha=0.3)
            plt.tight_layout()

            return plt.gcf()

        except Exception as e:
            logger.error(f"Scatter - Erro ao gerar gráfico de dispersão: {str(e)}", exc_info=True)
            return self._criar_grafico_sem_dados(f"{titulo} - Erro: {str(e)}")
