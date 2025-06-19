import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from utils.LogManager import LogManager
from .gst_01_base_gerador import BaseGerador


class GraficoBoxplot(BaseGerador):
    __slots__ = []

    def gerar(self):
        logger = LogManager.get_logger()
        logger.debug("Iniciando geração do gráfico boxplot")

        try:
            df = self._obter_dados()
            titulo = self.loc.get_text("size_distribution") if self.loc else 'Distribuição de Tamanhos'

            logger.debug(f"BoxPlot - Dados obtidos: {len(df)} registros")

            if 'tamanho' in df.columns:
                logger.debug(f"BoxPlot - Coluna tamanho encontrada, exemplo de valores: {df['tamanho'].head(5).tolist()}")

            else:
                logger.debug("BoxPlot - Coluna tamanho não encontrada no DataFrame")

            if df.empty:
                logger.warning("Dataset vazio para geração do boxplot")
                return self._criar_grafico_sem_dados(titulo)

            plt.figure(figsize=(14, 10))

            plt.subplot(2, 2, 1)
            self._criar_boxplot_operacoes(df)

            plt.subplot(2, 2, 2)
            self._criar_boxplot_tipos(df)

            plt.subplot(2, 2, 3)
            self._criar_boxplot_temporal(df)

            plt.subplot(2, 2, 4)
            self._criar_boxplot_tamanhos_categoria(df)

            plt.suptitle(titulo, fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            logger.debug("Gráfico boxplot criado com sucesso")
            return plt.gcf()

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico boxplot: {e}", exc_info=True)
            return self._criar_grafico_sem_dados(titulo if 'titulo' in locals() else "Distribuição de Tamanhos")

    def _converter_tamanho_para_numerico(self, df):
        logger = LogManager.get_logger()

        if 'tamanho' not in df.columns:
            logger.debug("BoxPlot - Coluna 'tamanho' não encontrada durante conversão")
            return df

        df_copy = df.copy()
        logger.debug(f"BoxPlot - Antes da conversão: {len(df_copy)} registros")

        try:
            df_copy['tamanho'] = df_copy['tamanho'].astype(str)
            df_copy['tamanho'] = df_copy['tamanho'].str.replace('[^0-9\.]', '', regex=True)
            df_copy['tamanho'] = pd.to_numeric(df_copy['tamanho'], errors='coerce')

            logger.debug(f"BoxPlot - Após conversão: {len(df_copy)} registros, {df_copy['tamanho'].notna().sum()} valores válidos")

            return df_copy

        except Exception as e:
            logger.error(f"Erro ao converter tamanhos para numérico: {e}", exc_info=True)
            return df

    def _filtrar_dados_com_tamanho_valido(self, df):
        logger = LogManager.get_logger()
        logger.debug(f"BoxPlot - Filtrando dados com tamanho válido de {len(df)} registros")

        try:
            if 'tamanho' not in df.columns and len(df) > 0:
                logger.debug("BoxPlot - Coluna 'tamanho' ausente, tentando alternativas")

                colunas_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
                if colunas_numericas:
                    logger.debug(f"BoxPlot - Usando coluna alternativa: {colunas_numericas[0]}")
                    df_copy = df.copy()
                    df_copy['tamanho'] = df_copy[colunas_numericas[0]]
                    return df_copy

                else:
                    logger.debug("BoxPlot - Nenhuma coluna numérica encontrada para substituir 'tamanho'")
                    df_copy = df.copy()
                    df_copy['tamanho'] = 1
                    return df_copy

            df_convertido = self._converter_tamanho_para_numerico(df)

            df_com_tamanho = df_convertido.dropna(subset=['tamanho'])
            logger.debug(f"BoxPlot - Após remover NaNs: {len(df_com_tamanho)} registros")

            if df_com_tamanho.empty and not df.empty:
                logger.debug("BoxPlot - Todos os valores são inválidos, usando valores simulados")
                df_dummy = df.copy()
                df_dummy['tamanho'] = 1
                return df_dummy

            df_positivo = df_com_tamanho[df_com_tamanho['tamanho'] > 0]
            logger.debug(f"BoxPlot - Após filtrar positivos: {len(df_positivo)} registros")

            if df_positivo.empty and not df_com_tamanho.empty:
                logger.debug("BoxPlot - Sem valores positivos, usando valores absolutos")
                df_com_tamanho['tamanho'] = df_com_tamanho['tamanho'].abs()
                df_positivo = df_com_tamanho[df_com_tamanho['tamanho'] > 0]

            return df_positivo

        except Exception as e:
            logger.error(f"Erro ao filtrar dados com tamanho válido: {e}", exc_info=True)
            return df

    def _criar_boxplot_operacoes(self, df):
        logger = LogManager.get_logger()
        logger.debug("BoxPlot - Iniciando criação do boxplot de operações")

        try:
            if 'tipo_operacao' not in df.columns:
                logger.debug("BoxPlot - Coluna tipo_operacao não encontrada. Criando operação simulada.")
                df_temp = df.copy()
                df_temp['tipo_operacao'] = 'Desconhecido'
                df = df_temp

            df_com_tamanho = self._filtrar_dados_com_tamanho_valido(df)
            logger.debug(f"BoxPlot - Operações: Dados filtrados: {len(df_com_tamanho)} registros")

            if df_com_tamanho.empty:
                logger.warning("BoxPlot - Operações: Sem dados válidos para plotar")
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados de tamanho', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("operation_type") if self.loc else 'Por Tipo de Operação')
                return

            df_com_tamanho = df_com_tamanho.copy()
            df_com_tamanho['tamanho_mb'] = df_com_tamanho['tamanho'] / (1024 * 1024)

            operacoes = df_com_tamanho['tipo_operacao'].unique()
            dados_boxplot = []
            labels = []

            for operacao in operacoes:
                tamanhos = df_com_tamanho[df_com_tamanho['tipo_operacao'] == operacao]['tamanho_mb']
                if len(tamanhos) > 0:
                    dados_boxplot.append(tamanhos)
                    labels.append(operacao)
                    logger.debug(f"BoxPlot - Operações: {operacao} tem {len(tamanhos)} registros")

            if dados_boxplot:
                cores = [self.cores_operacoes.get(label, '#333333') for label in labels]

                box_plot = plt.boxplot(dados_boxplot, labels=labels, patch_artist=True)

                for patch, cor in zip(box_plot['boxes'], cores):
                    patch.set_facecolor(cor)
                    patch.set_alpha(0.7)

                plt.yscale('log')
                plt.ylabel(self.loc.get_text("size") + ' (MB)' if self.loc else 'Tamanho (MB)')
                plt.title(self.loc.get_text("operation_type") if self.loc else 'Por Tipo de Operação')
                plt.xticks(rotation=45, ha='right')
                plt.grid(True, alpha=0.3)
                logger.debug("BoxPlot - Operações: Gráfico criado com sucesso")

            else:
                logger.warning("BoxPlot - Operações: Sem dados para boxplot após filtragem")
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados válidos', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("operation_type") if self.loc else 'Por Tipo de Operação')

        except Exception as e:
            logger.error(f"BoxPlot - Erro ao criar boxplot de operações: {e}", exc_info=True)
            plt.text(0.5, 0.5, f'Erro: {str(e)}', horizontalalignment='center', 
                    verticalalignment='center', transform=plt.gca().transAxes)
            plt.title(self.loc.get_text("operation_type") if self.loc else 'Por Tipo de Operação')

    def _criar_boxplot_tipos(self, df):
        logger = LogManager.get_logger()
        logger.debug("BoxPlot - Iniciando criação do boxplot de tipos de arquivo")

        try:
            df_com_tamanho = self._filtrar_dados_com_tamanho_valido(df)

            if df_com_tamanho.empty:
                logger.warning("BoxPlot - Tipos: Sem dados válidos para plotar")
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados de tamanho', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("type") if self.loc else 'Por Tipo de Arquivo')
                return

            df_com_tamanho = df_com_tamanho.copy()
            df_com_tamanho['tamanho_mb'] = df_com_tamanho['tamanho'] / (1024 * 1024)

            tipos_principais = df_com_tamanho['tipo'].value_counts().head(8).index.tolist()
            logger.debug(f"BoxPlot - Tipos: Usando os {len(tipos_principais)} tipos mais comuns: {tipos_principais}")

            df_filtrado = df_com_tamanho[df_com_tamanho['tipo'].isin(tipos_principais)]

            dados_boxplot = []
            labels = []

            for tipo in tipos_principais:
                tamanhos = df_filtrado[df_filtrado['tipo'] == tipo]['tamanho_mb']
                if len(tamanhos) > 0:
                    dados_boxplot.append(tamanhos)
                    labels.append(tipo)
                    logger.debug(f"BoxPlot - Tipos: {tipo} tem {len(tamanhos)} registros")

            if dados_boxplot:
                cores = plt.cm.Set3(np.linspace(0, 1, len(labels)))

                box_plot = plt.boxplot(dados_boxplot, labels=labels, patch_artist=True)

                for patch, cor in zip(box_plot['boxes'], cores):
                    patch.set_facecolor(cor)
                    patch.set_alpha(0.7)

                plt.yscale('log')
                plt.ylabel(self.loc.get_text("size") + ' (MB)' if self.loc else 'Tamanho (MB)')
                plt.title(self.loc.get_text("type") if self.loc else 'Por Tipo de Arquivo')
                plt.xticks(rotation=45, ha='right')
                plt.grid(True, alpha=0.3)
                logger.debug("BoxPlot - Tipos: Gráfico criado com sucesso")

            else:
                logger.warning("BoxPlot - Tipos: Sem dados para boxplot após filtragem")
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados válidos', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("type") if self.loc else 'Por Tipo de Arquivo')

        except Exception as e:
            logger.error(f"BoxPlot - Erro ao criar boxplot de tipos: {e}", exc_info=True)
            plt.text(0.5, 0.5, f'Erro: {str(e)}', horizontalalignment='center', 
                    verticalalignment='center', transform=plt.gca().transAxes)
            plt.title(self.loc.get_text("type") if self.loc else 'Por Tipo de Arquivo')

    def _criar_boxplot_temporal(self, df):
        logger = LogManager.get_logger()
        logger.debug("BoxPlot - Iniciando criação do boxplot temporal")

        try:
            if 'timestamp' not in df.columns or df['timestamp'].isna().all():
                logger.warning("BoxPlot - Temporal: Coluna timestamp não encontrada ou com todos valores nulos")
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados temporais', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("hour_of_day") if self.loc else 'Por Hora do Dia')
                return

            df_temporal = df.copy()
            df_temporal['timestamp'] = pd.to_datetime(df_temporal['timestamp'], errors='coerce')
            logger.debug(f"BoxPlot - Temporal: Convertidas {df_temporal['timestamp'].notna().sum()} datas válidas")

            df_temporal = df_temporal.dropna(subset=['timestamp'])

            if df_temporal.empty:
                logger.warning("BoxPlot - Temporal: Sem dados temporais válidos após filtro")
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados temporais válidos', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("hour_of_day") if self.loc else 'Por Hora do Dia')
                return

            df_temporal['hora'] = df_temporal['timestamp'].dt.hour

            distribuicao_horas = df_temporal['hora'].value_counts().sort_index()
            logger.debug(f"BoxPlot - Temporal: Distribuição de eventos por hora: {dict(distribuicao_horas)}")

            eventos_por_hora = df_temporal.groupby(['hora', df_temporal['timestamp'].dt.date]).size().reset_index(name='count')
            logger.debug(f"BoxPlot - Temporal: Calculados eventos por hora/dia: {len(eventos_por_hora)} registros")

            horas = sorted(eventos_por_hora['hora'].unique())
            dados_boxplot = []

            for hora in horas:
                contagens = eventos_por_hora[eventos_por_hora['hora'] == hora]['count']
                if len(contagens) > 0:
                    dados_boxplot.append(contagens)
                    logger.debug(f"BoxPlot - Temporal: Hora {hora} tem {len(contagens)} dias com eventos")

            if dados_boxplot and len(horas) > 0:
                box_plot = plt.boxplot(dados_boxplot, labels=horas, patch_artist=True)

                cores = plt.cm.viridis(np.linspace(0, 1, len(horas)))

                for patch, cor in zip(box_plot['boxes'], cores):
                    patch.set_facecolor(cor)
                    patch.set_alpha(0.7)

                plt.xlabel(self.loc.get_text("hour_of_day") if self.loc else 'Hora do Dia')
                plt.ylabel(self.loc.get_text("events_monitored") if self.loc else 'Eventos por Dia')
                plt.title(self.loc.get_text("hour_of_day") if self.loc else 'Distribuição por Hora')
                plt.grid(True, alpha=0.3)
                logger.debug("BoxPlot - Temporal: Gráfico criado com sucesso")

            else:
                logger.warning("BoxPlot - Temporal: Sem dados suficientes para gráfico")
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados temporais suficientes', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("hour_of_day") if self.loc else 'Por Hora do Dia')

        except Exception as e:
            logger.error(f"BoxPlot - Erro ao criar boxplot temporal: {e}", exc_info=True)
            plt.text(0.5, 0.5, f'Erro: {str(e)}', horizontalalignment='center', 
                    verticalalignment='center', transform=plt.gca().transAxes)
            plt.title(self.loc.get_text("hour_of_day") if self.loc else 'Por Hora do Dia')

    def _criar_boxplot_tamanhos_categoria(self, df):
        logger = LogManager.get_logger()
        logger.debug("BoxPlot - Iniciando criação do boxplot de categorias de tamanho")

        try:
            df_com_tamanho = self._filtrar_dados_com_tamanho_valido(df)

            if df_com_tamanho.empty:
                logger.warning("BoxPlot - Categorias: Sem dados válidos para plotar")
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados de tamanho', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("size_categories") if self.loc else 'Categorias de Tamanho')
                return

            df_categorizado = df_com_tamanho.copy()
            df_categorizado['categoria_tamanho'] = df_categorizado['tamanho'].apply(self._categorizar_tamanho)
            df_categorizado['tamanho_mb'] = df_categorizado['tamanho'] / (1024 * 1024)

            distribuicao = df_categorizado['categoria_tamanho'].value_counts().to_dict()
            logger.debug(f"BoxPlot - Categorias: Distribuição: {distribuicao}")

            categorias = [
                self.loc.get_text("very_small") if self.loc else 'Muito Pequeno',
                self.loc.get_text("small") if self.loc else 'Pequeno',
                self.loc.get_text("medium") if self.loc else 'Médio',
                self.loc.get_text("large") if self.loc else 'Grande',
                self.loc.get_text("very_large") if self.loc else 'Muito Grande'
            ]

            mapeamento_categorias = {
                'Muito Pequeno': self.loc.get_text("very_small") if self.loc else 'Muito Pequeno',
                'Pequeno': self.loc.get_text("small") if self.loc else 'Pequeno',
                'Médio': self.loc.get_text("medium") if self.loc else 'Médio',
                'Grande': self.loc.get_text("large") if self.loc else 'Grande',
                'Muito Grande': self.loc.get_text("very_large") if self.loc else 'Muito Grande'
            }

            dados_boxplot = []
            labels_existentes = []

            for categoria_original, categoria_traduzida in mapeamento_categorias.items():
                tamanhos = df_categorizado[df_categorizado['categoria_tamanho'] == categoria_original]['tamanho_mb']
                if len(tamanhos) > 0:
                    dados_boxplot.append(tamanhos)
                    labels_existentes.append(categoria_traduzida)
                    logger.debug(f"BoxPlot - Categorias: {categoria_original} tem {len(tamanhos)} registros")

            if dados_boxplot:
                cores = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3', '#a6d854'][:len(labels_existentes)]

                box_plot = plt.boxplot(dados_boxplot, labels=labels_existentes, patch_artist=True)

                for patch, cor in zip(box_plot['boxes'], cores):
                    patch.set_facecolor(cor)
                    patch.set_alpha(0.7)

                plt.yscale('log')
                plt.ylabel(self.loc.get_text("size") + ' (MB)' if self.loc else 'Tamanho (MB)')
                plt.title(self.loc.get_text("size_categories") if self.loc else 'Categorias de Tamanho')
                plt.xticks(rotation=45, ha='right')
                plt.grid(True, alpha=0.3)
                logger.debug("BoxPlot - Categorias: Gráfico criado com sucesso")

            else:
                logger.warning("BoxPlot - Categorias: Sem dados para boxplot após filtragem")
                plt.text(0.5, 0.5, self.loc.get_text("no_data_to_plot") if self.loc else 'Sem dados válidos', 
                        horizontalalignment='center', verticalalignment='center', transform=plt.gca().transAxes)
                plt.title(self.loc.get_text("size_categories") if self.loc else 'Categorias de Tamanho')

        except Exception as e:
            logger.error(f"BoxPlot - Erro ao criar boxplot de categorias: {e}", exc_info=True)
            plt.text(0.5, 0.5, f'Erro: {str(e)}', horizontalalignment='center', 
                    verticalalignment='center', transform=plt.gca().transAxes)
            plt.title(self.loc.get_text("size_categories") if self.loc else 'Categorias de Tamanho')

    def _categorizar_tamanho(self, tamanho_bytes):
        try:
            tamanho = float(tamanho_bytes)

            if tamanho < 1024:
                return 'Muito Pequeno'

            elif tamanho < 1024 * 1024:
                return 'Pequeno'

            elif tamanho < 100 * 1024 * 1024:
                return 'Médio'

            elif tamanho < 1024 * 1024 * 1024:
                return 'Grande'

            else:
                return 'Muito Grande'

        except (ValueError, TypeError) as e:
            LogManager.get_logger().debug(f"Erro ao categorizar tamanho '{tamanho_bytes}': {e}")
            return 'Desconhecido'
