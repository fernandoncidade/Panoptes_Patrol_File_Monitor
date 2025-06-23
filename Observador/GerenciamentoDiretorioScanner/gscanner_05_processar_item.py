import sqlite3
from datetime import datetime

def _processar_item(self, nome, caminho, tipo):
    try:
        metadados = self.gerenciador_colunas.get_metadados({
            "nome": nome,
            "dir_atual": caminho
        })

        tipo = self.get_file_type(caminho)

        with self.lock_db:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                        INSERT INTO snapshot (
                                nome,
                                diretorio,
                                tipo,
                                data_criacao,
                                data_modificacao,
                                data_acesso,
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
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        nome,
                        caminho,
                        tipo,
                        metadados.get("data_criacao", ""),
                        metadados.get("data_modificacao", ""),
                        metadados.get("data_acesso", ""),
                        metadados.get("tamanho", ""),
                        metadados.get("atributos", ""),
                        metadados.get("autor", ""),
                        metadados.get("dimensoes", ""),
                        metadados.get("duracao", ""),
                        metadados.get("taxa_bits", ""),
                        metadados.get("protegido", ""),
                        metadados.get("paginas", ""),
                        metadados.get("linhas", ""),
                        metadados.get("palavras", ""),
                        metadados.get("paginas_estimadas", ""),
                        metadados.get("linhas_codigo", ""),
                        metadados.get("total_linhas", ""),
                        metadados.get("slides_estimados", ""),
                        metadados.get("arquivos", ""),
                        metadados.get("descompactados", ""),
                        metadados.get("slides", ""),
                        metadados.get("binario", ""),
                        metadados.get("planilhas", ""),
                        metadados.get("colunas", ""),
                        metadados.get("registros", ""),
                        metadados.get("tabelas", ""),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))

                conn.commit()

    except Exception as e:
        print(f"Erro ao processar item {nome}: {e}")
