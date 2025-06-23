import sqlite3
from datetime import datetime

def registrar_evento_especifico(self, tabela, evento):
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {tabela} (
                    nome,
                    dir_anterior,
                    dir_atual,
                    data_criacao,
                    data_modificacao,
                    data_acesso,
                    tipo,
                    tamanho,
                    atributos,
                    autor,
                    dimensoes,
                    duracao,
                    taxa_bits,
                    protegido,
                    paginas,
                    linhas,
                    palavras,
                    paginas_estimadas,
                    linhas_codigo,
                    total_linhas,
                    slides_estimados,
                    arquivos,
                    descompactados,
                    slides,
                    binario,
                    planilhas,
                    colunas,
                    registros,
                    tabelas,
                    timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evento["nome"],
                evento.get("dir_anterior", ""),
                evento.get("dir_atual", ""),
                evento.get("data_criacao", ""),
                evento.get("data_modificacao", ""),
                evento.get("data_acesso", ""),
                evento["tipo"],
                evento.get("tamanho", ""),
                evento.get("atributos", ""),
                evento.get("autor", ""),
                evento.get("dimensoes", ""),
                evento.get("duracao", ""),
                evento.get("taxa_bits", ""),
                evento.get("protegido", ""),
                evento.get("paginas", ""),
                evento.get("linhas", ""),
                evento.get("palavras", ""),
                evento.get("paginas_estimadas", ""),
                evento.get("linhas_codigo", ""),
                evento.get("total_linhas", ""),
                evento.get("slides_estimados", ""),
                evento.get("arquivos", ""),
                evento.get("descompactados", ""),
                evento.get("slides", ""),
                evento.get("binario", ""),
                evento.get("planilhas", ""),
                evento.get("colunas", ""),
                evento.get("registros", ""),
                evento.get("tabelas", ""),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()

    except Exception as e:
        print(f"Erro ao registrar evento na tabela {tabela}: {e}")
