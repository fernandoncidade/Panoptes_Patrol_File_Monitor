import os
import logging
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from .GeradorEstatisticas import (BaseGerador, GraficoPizza, GraficoBarras, GraficoTimeline, 
                                  GraficoTreemap, GraficoHistograma, GraficoPareto, GraficoLinha, 
                                  GraficoBoxplot, GraficoRadarEventos, GraficoHeatmap, GraficoScatter, 
                                  GraficoSankey, GraficoRadar, GraficoDotplot)


class GeradorEstatisticas:
    __slots__ = ['db_path', 'loc', 'interface', '_geradores']

    def __init__(self, db_path, localizador=None, interface_principal=None):
        self.db_path = db_path
        self.loc = localizador
        self.interface = interface_principal
        self._geradores = {}

        self._inicializar_geradores()

    def _inicializar_geradores(self):
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

        for nome, classe in geradores_classes.items():
            self._geradores[nome] = classe(self.db_path, self.loc, self.interface)

    def _obter_dados(self):
        if self._geradores:
            primeiro_nome = next(iter(self._geradores))
            return self._geradores[primeiro_nome]._obter_dados()

        query = """
            SELECT tipo_operacao, tipo, timestamp, tamanho 
            FROM monitoramento 
            WHERE timestamp IS NOT NULL
        """
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(query, conn)

        return df

    def atualizar_textos_traduzidos(self):
        for gerador in self._geradores.values():
            if hasattr(gerador, '_atualizar_textos_traduzidos'):
                gerador._atualizar_textos_traduzidos()

    def adicionar_gerador(self, nome, classe_gerador):
        if hasattr(classe_gerador, '__slots__'):
            self._geradores[nome] = classe_gerador(self.db_path, self.loc, self.interface)

        else:
            raise ValueError("Gerador deve usar __slots__ para consistência")

    def remover_gerador(self, nome):
        if nome in self._geradores:
            del self._geradores[nome]

    def listar_geradores(self):
        return list(self._geradores.keys())

    def grafico_operacoes_pizza(self):
        return self._geradores['pizza'].gerar()

    def grafico_tipos_arquivo_barras(self):
        return self._geradores['barras'].gerar()

    def grafico_timeline_operacoes(self):
        return self._geradores['timeline'].gerar()

    def grafico_treemap_tipos(self):
        return self._geradores['treemap'].gerar()

    def grafico_histograma_horarios(self):
        return self._geradores['histograma'].gerar()

    def grafico_pareto_operacoes(self):
        return self._geradores['pareto'].gerar()

    def grafico_cluster_linha(self):
        return self._geradores['linha'].gerar()
    
    def grafico_boxplot_distribuicao(self):
        return self._geradores['boxplot'].gerar()

    def grafico_boxplot_eventos(self):
        return self._geradores['boxplot_eventos'].gerar()

    def grafico_heatmap(self):
        return self._geradores['heatmap'].gerar()

    def grafico_scatter(self):
        return self._geradores['scatter'].gerar()

    def grafico_sankey(self):
        return self._geradores['sankey'].gerar()

    def grafico_radar(self):
        return self._geradores['radar'].gerar()

    def grafico_dotplot(self):
        return self._geradores['dotplot'].gerar()

    def gerar_grafico(self, tipo_grafico):
        if tipo_grafico in self._geradores:
            return self._geradores[tipo_grafico].gerar()

        else:
            raise ValueError(f"Tipo de gráfico '{tipo_grafico}' não encontrado")

    def salvar_graficos(self, diretorio):
        logger = logging.getLogger('FileManager')

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

        if not os.path.exists(diretorio):
            try:
                os.makedirs(diretorio, exist_ok=True)
                logger.info(f"Diretório {diretorio} criado com sucesso")

            except Exception as e:
                logger.error(f"Erro ao criar diretório {diretorio}: {e}")
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
                    logger.error(f"Erro ao salvar {nome}: {e}")
                    resultados[nome] = False

                finally:
                    plt.close(fig)
                    plt.clf()
                    plt.cla()

            except Exception as e:
                logger.error(f"Erro ao processar gráfico {nome}: {e}")
                resultados[nome] = False

        plt.close('all')
        return resultados
