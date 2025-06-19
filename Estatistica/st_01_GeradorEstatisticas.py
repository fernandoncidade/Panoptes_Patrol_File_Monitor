import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from utils.LogManager import LogManager
from .GeradorEstatisticas import (BaseGerador, GraficoPizza, GraficoBarras, GraficoTimeline, 
                                  GraficoTreemap, GraficoHistograma, GraficoPareto, GraficoLinha, 
                                  GraficoBoxplot, GraficoRadarEventos, GraficoHeatmap, GraficoScatter, 
                                  GraficoSankey, GraficoRadar, GraficoDotplot)


class GeradorEstatisticas:
    __slots__ = ['db_path', 'loc', 'interface', '_geradores']

    def __init__(self, db_path, localizador=None, interface_principal=None):
        logger = LogManager.get_logger()
        logger.debug(f"Inicializando GeradorEstatisticas com banco de dados: {db_path}")

        self.db_path = db_path
        self.loc = localizador
        self.interface = interface_principal
        self._geradores = {}

        self._inicializar_geradores()
        logger.info("GeradorEstatisticas inicializado com sucesso")

    def _inicializar_geradores(self):
        logger = LogManager.get_logger()
        logger.debug("Inicializando geradores de gráficos")

        geradores_classes = {
            'pizza': GraficoPizza,
            'barras': GraficoBarras,
            'timeline': GraficoTimeline,
            'treemap': GraficoTreemap,
            'histograma': GraficoHistograma,
            'pareto': GraficoPareto,
            'linha': GraficoLinha,
            'boxplot': GraficoBoxplot,
            'boxplot_eventos': GraficoRadarEventos,
            'heatmap': GraficoHeatmap,
            'scatter': GraficoScatter,
            'sankey': GraficoSankey,
            'radar': GraficoRadar,
            'dotplot': GraficoDotplot
        }

        try:
            for nome, classe in geradores_classes.items():
                self._geradores[nome] = classe(self.db_path, self.loc, self.interface)
                logger.debug(f"Gerador '{nome}' inicializado")

        except Exception as e:
            logger.error(f"Erro ao inicializar geradores: {e}", exc_info=True)

        logger.info(f"Total de {len(self._geradores)} geradores inicializados")

    def _obter_dados(self):
        logger = LogManager.get_logger()
        logger.debug("Obtendo dados para geração de gráficos")

        try:
            if self._geradores:
                primeiro_nome = next(iter(self._geradores))
                logger.debug(f"Usando gerador '{primeiro_nome}' para obter dados")
                return self._geradores[primeiro_nome]._obter_dados()

            query = """
                SELECT tipo_operacao, tipo, timestamp, tamanho 
                FROM monitoramento 
                WHERE timestamp IS NOT NULL
            """

            logger.debug(f"Executando query SQL: {query}")

            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn)

            logger.debug(f"Dados obtidos com sucesso: {len(df)} registros")
            return df

        except Exception as e:
            logger.error(f"Erro ao obter dados: {e}", exc_info=True)
            return pd.DataFrame()

    def atualizar_textos_traduzidos(self):
        logger = LogManager.get_logger()
        logger.debug("Atualizando textos traduzidos nos geradores")

        try:
            for nome, gerador in self._geradores.items():
                if hasattr(gerador, '_atualizar_textos_traduzidos'):
                    gerador._atualizar_textos_traduzidos()
                    logger.debug(f"Textos traduzidos atualizados para gerador '{nome}'")

        except Exception as e:
            logger.error(f"Erro ao atualizar textos traduzidos: {e}", exc_info=True)

    def adicionar_gerador(self, nome, classe_gerador):
        logger = LogManager.get_logger()
        logger.debug(f"Adicionando novo gerador '{nome}'")

        try:
            if hasattr(classe_gerador, '__slots__'):
                self._geradores[nome] = classe_gerador(self.db_path, self.loc, self.interface)
                logger.info(f"Gerador '{nome}' adicionado com sucesso")

            else:
                msg = "Gerador deve usar __slots__ para consistência"
                logger.error(msg)
                raise ValueError(msg)

        except Exception as e:
            logger.error(f"Erro ao adicionar gerador '{nome}': {e}", exc_info=True)
            raise

    def remover_gerador(self, nome):
        logger = LogManager.get_logger()

        try:
            if nome in self._geradores:
                del self._geradores[nome]
                logger.info(f"Gerador '{nome}' removido com sucesso")

            else:
                logger.warning(f"Tentativa de remover gerador inexistente: '{nome}'")

        except Exception as e:
            logger.error(f"Erro ao remover gerador '{nome}': {e}", exc_info=True)

    def listar_geradores(self):
        logger = LogManager.get_logger()
        logger.debug("Listando geradores disponíveis")
        return list(self._geradores.keys())

    def grafico_operacoes_pizza(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico de pizza de operações")

        try:
            return self._geradores['pizza'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de pizza: {e}", exc_info=True)
            raise

    def grafico_tipos_arquivo_barras(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico de barras de tipos de arquivo")

        try:
            return self._geradores['barras'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de barras: {e}", exc_info=True)
            raise

    def grafico_timeline_operacoes(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico timeline de operações")

        try:
            return self._geradores['timeline'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico timeline: {e}", exc_info=True)
            raise

    def grafico_treemap_tipos(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico treemap de tipos")

        try:
            return self._geradores['treemap'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico treemap: {e}", exc_info=True)
            raise

    def grafico_histograma_horarios(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando histograma de horários")

        try:
            return self._geradores['histograma'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar histograma: {e}", exc_info=True)
            raise

    def grafico_pareto_operacoes(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico de pareto de operações")

        try:
            return self._geradores['pareto'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de pareto: {e}", exc_info=True)
            raise

    def grafico_cluster_linha(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico de linha de cluster")

        try:
            return self._geradores['linha'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de linha: {e}", exc_info=True)
            raise
    
    def grafico_boxplot_distribuicao(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico boxplot de distribuição")

        try:
            return self._geradores['boxplot'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar boxplot: {e}", exc_info=True)
            raise

    def grafico_boxplot_eventos(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico boxplot de eventos")

        try:
            return self._geradores['boxplot_eventos'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar boxplot de eventos: {e}", exc_info=True)
            raise

    def grafico_heatmap(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico heatmap")

        try:
            return self._geradores['heatmap'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar heatmap: {e}", exc_info=True)
            raise

    def grafico_scatter(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico scatter")

        try:
            return self._geradores['scatter'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar scatter: {e}", exc_info=True)
            raise

    def grafico_sankey(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico sankey")

        try:
            return self._geradores['sankey'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar sankey: {e}", exc_info=True)
            raise

    def grafico_radar(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico radar")

        try:
            return self._geradores['radar'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar radar: {e}", exc_info=True)
            raise

    def grafico_dotplot(self):
        logger = LogManager.get_logger()
        logger.debug("Gerando gráfico dotplot")

        try:
            return self._geradores['dotplot'].gerar()

        except Exception as e:
            logger.error(f"Erro ao gerar dotplot: {e}", exc_info=True)
            raise

    def gerar_grafico(self, tipo_grafico):
        logger = LogManager.get_logger()
        logger.debug(f"Solicitação para gerar gráfico do tipo: {tipo_grafico}")
        
        try:
            if tipo_grafico in self._geradores:
                logger.info(f"Gerando gráfico do tipo: {tipo_grafico}")
                return self._geradores[tipo_grafico].gerar()

            else:
                msg = f"Tipo de gráfico '{tipo_grafico}' não encontrado"
                logger.error(msg)
                raise ValueError(msg)

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico '{tipo_grafico}': {e}", exc_info=True)
            raise

    def salvar_graficos(self, diretorio):
        logger = LogManager.get_logger()
        logger.info(f"Iniciando salvamento de todos os gráficos no diretório: {diretorio}")

        graficos = {
            self.loc.get_text("operations_pie") if self.loc else "operations_pie": self.grafico_operacoes_pizza,
            self.loc.get_text("file_types") if self.loc else "file_types": self.grafico_tipos_arquivo_barras,
            self.loc.get_text("timeline") if self.loc else "timeline": self.grafico_timeline_operacoes,
            self.loc.get_text("tree_map") if self.loc else "tree_map": self.grafico_treemap_tipos,
            self.loc.get_text("hour_histogram") if self.loc else "hour_histogram": self.grafico_histograma_horarios,
            self.loc.get_text("pareto_analysis") if self.loc else "pareto_analysis": self.grafico_pareto_operacoes,
            self.loc.get_text("operations_by_day") if self.loc else "operations_by_day": self.grafico_cluster_linha,
            self.loc.get_text("size_distribution") if self.loc else "size_distribution": self.grafico_boxplot_distribuicao,
            self.loc.get_text("events_monitored") if self.loc else "events_monitored": self.grafico_boxplot_eventos,
            self.loc.get_text("temporal_distribution") if self.loc else "temporal_distribution": self.grafico_heatmap,
            self.loc.get_text("file_size_analysis") if self.loc else "file_size_analysis": self.grafico_scatter,
            self.loc.get_text("file_operations_flow") if self.loc else "file_operations_flow": self.grafico_sankey,
            self.loc.get_text("operations_by_file_type") if self.loc else "operations_by_file_type": self.grafico_radar,
            self.loc.get_text("file_size_distribution") if self.loc else "file_size_distribution": self.grafico_dotplot
        }

        resultados = {}
        logger.debug(f"Total de {len(graficos)} gráficos para salvar")

        if not os.path.exists(diretorio):
            try:
                os.makedirs(diretorio, exist_ok=True)
                logger.info(f"Diretório {diretorio} criado com sucesso")

            except Exception as e:
                logger.error(f"Erro ao criar diretório {diretorio}: {e}", exc_info=True)
                return {nome: False for nome in graficos.keys()}

        if not os.access(diretorio, os.W_OK):
            logger.error(f"Sem permissão de escrita no diretório {diretorio}")
            return {nome: False for nome in graficos.keys()}

        for nome, func in graficos.items():
            try:
                logger.debug(f"Gerando gráfico {nome}...")
                fig = func()
                arquivo_destino = os.path.join(diretorio, f"{nome}.png")
                logger.debug(f"Salvando {nome} em {arquivo_destino}")

                try:
                    fig.savefig(arquivo_destino, bbox_inches='tight', dpi=100)
                    logger.info(f"Gráfico {nome} salvo com sucesso")
                    resultados[nome] = True

                except Exception as e:
                    logger.error(f"Erro ao salvar gráfico {nome}: {e}", exc_info=True)
                    resultados[nome] = False

                finally:
                    plt.close(fig)
                    plt.clf()
                    plt.cla()

            except Exception as e:
                logger.error(f"Erro ao processar gráfico {nome}: {e}", exc_info=True)
                resultados[nome] = False

        plt.close('all')
        logger.info(f"Processo de salvamento de gráficos concluído. {sum(resultados.values())} de {len(resultados)} salvos com sucesso.")
        return resultados
