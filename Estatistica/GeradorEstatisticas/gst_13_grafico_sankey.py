import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from utils.LogManager import LogManager
from .gst_01_base_gerador import BaseGerador

try:
    import plotly.graph_objects as go
    from plotly.io import to_image
    PLOTLY_AVAILABLE = True
    LogManager.get_logger().info("Biblioteca plotly disponível para gráficos Sankey")

except ImportError:
    PLOTLY_AVAILABLE = False
    LogManager.get_logger().warning("Biblioteca plotly não disponível - gráficos Sankey serão limitados")


class GraficoSankey(BaseGerador):
    __slots__ = []

    def gerar(self):
        logger = LogManager.get_logger()
        logger.debug("Iniciando geração do diagrama de Sankey")

        df = self._obter_dados()
        titulo = self.loc.get_text("file_operations_flow") if self.loc else 'Fluxo de Operações em Arquivos'

        logger.debug(f"Sankey - Dados obtidos: {len(df)} registros")

        if df.empty:
            logger.warning("Dataset vazio para geração do diagrama de Sankey")
            return self._criar_grafico_sem_dados(titulo)

        if not PLOTLY_AVAILABLE:
            logger.warning("Biblioteca plotly não disponível para gerar o diagrama de Sankey")
            plt.figure(figsize=(12, 8))
            mensagem = self.loc.get_text("plotly_required") if self.loc else 'Biblioteca plotly necessária para\ngerar o Diagrama de Sankey\n\npip install plotly'
            plt.text(0.5, 0.5, mensagem,
                    ha='center', va='center', fontsize=14)
            plt.axis('off')
            return plt.gcf()

        try:
            df_sankey = df[['tipo_operacao', 'tipo']].copy()
            df_sankey = df_sankey.dropna()

            registros_removidos = len(df) - len(df_sankey)
            if registros_removidos > 0:
                logger.debug(f"Sankey - {registros_removidos} registros removidos por terem valores nulos")

            if df_sankey.empty:
                logger.warning("Sankey - Sem dados válidos após filtrar valores nulos")
                return self._criar_grafico_sem_dados(titulo)

            operacoes_top = df_sankey['tipo_operacao'].value_counts().nlargest(6).index.tolist()
            tipos_top = df_sankey['tipo'].value_counts().nlargest(10).index.tolist()

            logger.debug(f"Sankey - Top 6 operações: {operacoes_top}")
            logger.debug(f"Sankey - Top 10 tipos de arquivo: {tipos_top}")

            df_sankey = df_sankey[
                (df_sankey['tipo_operacao'].isin(operacoes_top)) & 
                (df_sankey['tipo'].isin(tipos_top))
            ]

            logger.debug(f"Sankey - {len(df_sankey)} registros após filtrar para os tipos mais comuns")

            fluxos = df_sankey.groupby(['tipo_operacao', 'tipo']).size().reset_index(name='valor')
            logger.debug(f"Sankey - {len(fluxos)} fluxos distintos identificados")

            todas_labels = list(set(operacoes_top) | set(tipos_top))
            mapa_indices = {label: i for i, label in enumerate(todas_labels)}

            fonte = [mapa_indices[op] for op in fluxos['tipo_operacao']]
            destino = [mapa_indices[tipo] for tipo in fluxos['tipo']]
            valores = fluxos['valor'].tolist()

            logger.debug(f"Sankey - Preparando cores para {len(operacoes_top)} operações e {len(tipos_top)} tipos")
            cores_ops = [self.cores_operacoes.get(op, '#333333') for op in operacoes_top]
            cores_tipos = ['#' + ''.join([hex(int(np.random.rand() * 200 + 55))[2:].zfill(2) for _ in range(3)]) for _ in range(len(tipos_top))]
            cores_links = cores_ops * len(tipos_top)

            logger.debug("Sankey - Criando figura Plotly")
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=todas_labels,
                    color=cores_ops + cores_tipos
                ),
                link=dict(
                    source=fonte,
                    target=destino,
                    value=valores,
                    color=[f"rgba({int(color[1:3], 16)}, {int(color[3:5], 16)}, {int(color[5:7], 16)}, 0.5)" for color in cores_links]
                )
            )])

            fig.update_layout(
                title_text=titulo,
                font_size=14,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )

            logger.debug("Sankey - Convertendo figura Plotly para imagem")
            img_bytes = to_image(fig, format='png', scale=2)

            from io import BytesIO
            from PIL import Image

            img = Image.open(BytesIO(img_bytes))
            plt.figure(figsize=(12, 8))
            plt.imshow(np.array(img))
            plt.axis('off')

            logger.debug("Sankey - Diagrama gerado com sucesso")
            return plt.gcf()

        except Exception as e:
            logger.error(f"Sankey - Erro ao gerar diagrama de Sankey: {e}", exc_info=True)
            return self._criar_grafico_sem_dados(f"{titulo} - Erro: {str(e)}")
