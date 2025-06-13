import matplotlib.pyplot as plt
import squarify
from .gst_01_base_gerador import BaseGerador


class GraficoTreemap(BaseGerador):
    __slots__ = []

    def gerar(self):
        df = self._obter_dados()
        titulo = self.loc.get_text("tree_map") if self.loc else 'Mapa de Árvore - Tipos de Arquivo'

        if df.empty:
            return self._criar_grafico_sem_dados(titulo)

        tipos = df['tipo'].value_counts()[:30]
        if not tipos.empty:
            plt.figure(figsize=(12, 8))
            squarify.plot(sizes=tipos.values, label=tipos.index, alpha=0.6)
            plt.title(titulo)
            plt.axis('off')

        return plt.gcf()
