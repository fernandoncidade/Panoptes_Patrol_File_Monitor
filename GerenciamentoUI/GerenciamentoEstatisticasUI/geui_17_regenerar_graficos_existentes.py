from PySide6.QtWidgets import QVBoxLayout
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from utils.LogManager import LogManager

logger = LogManager.get_logger()

def _regenerar_graficos_existentes(self, graficos_atualizados, mapeamento_funcoes):
    try:
        if not self.tab_widget:
            return

        for i in range(self.tab_widget.count()):
            titulo_atual = self.tab_widget.tabText(i)

            func_correspondente = None
            for titulo_antigo, data in self.checkboxes_graficos.items():
                if titulo_antigo == titulo_atual or mapeamento_funcoes.get(data['grafico_data']['func']) == titulo_atual:
                    func_correspondente = data['grafico_data']['func']
                    break

            if func_correspondente:
                grafico_atualizado = None
                for grafico in graficos_atualizados:
                    if grafico['func'] == func_correspondente:
                        grafico_atualizado = grafico
                        break

                if grafico_atualizado:
                    try:
                        logger.debug(f"Regenerando gráfico: {grafico_atualizado['titulo']}")
                        nova_fig = grafico_atualizado["func"]()

                        self.graficos_dados[grafico_atualizado["titulo"]] = {'fig': nova_fig, 'func': grafico_atualizado["func"], 'titulo': grafico_atualizado["titulo"]}

                        novo_canvas = FigureCanvas(nova_fig)

                        tab_atual = self.tab_widget.widget(i)
                        if tab_atual:
                            layout_atual = tab_atual.layout()
                            if layout_atual:
                                while layout_atual.count():
                                    child = layout_atual.takeAt(0)
                                    if child.widget():
                                        child.widget().deleteLater()

                                layout_atual.addWidget(novo_canvas)

                            else:
                                novo_layout = QVBoxLayout()
                                novo_layout.addWidget(novo_canvas)
                                tab_atual.setLayout(novo_layout)

                        self.tab_widget.setTabText(i, grafico_atualizado["titulo"])

                    except Exception as e:
                        logger.error(f"Erro ao regenerar gráfico {grafico_atualizado['titulo']}: {e}", exc_info=True)

    except Exception as e:
        logger.error(f"Erro ao regenerar gráficos existentes: {e}", exc_info=True)
