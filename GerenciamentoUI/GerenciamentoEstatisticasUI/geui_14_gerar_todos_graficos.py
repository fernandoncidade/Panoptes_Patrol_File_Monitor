from PySide6.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _gerar_todos_graficos(self, graficos):
    self.graficos_dados.clear()
    for grafico in graficos:
        try:
            logger.debug(f"Gerando gráfico: {grafico['titulo']}")
            fig = grafico["func"]()

            self.graficos_dados[grafico["titulo"]] = {'fig': fig, 'func': grafico["func"], 'titulo': grafico["titulo"]}

            canvas = FigureCanvas(fig)
            tab = QWidget()
            tab_layout = QVBoxLayout()
            tab_layout.addWidget(canvas)
            tab.setLayout(tab_layout)
            self.tab_widget.addTab(tab, grafico["titulo"])

        except Exception as e:
            logger.error(f"Erro ao gerar gráfico {grafico['titulo']}: {e}", exc_info=True)
