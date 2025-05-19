import sqlite3
from datetime import datetime

def _process_batch(self, batch):
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            for nome, caminho, _ in batch:
                try:
                    tipo = self.get_file_type(caminho)

                    metadados = self.gerenciador_colunas.get_metadados({
                        "nome": nome,
                        "dir_atual": caminho
                    })

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

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("""
                        INSERT INTO escaneado (
                                tipo_operacao,
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
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        self.observador.loc.get_text("op_scanned"),
                        nome,
                        "",
                        caminho,
                        metadados.get("data_criacao", ""),
                        metadados.get("data_modificacao", ""),
                        metadados.get("data_acesso", ""),
                        tipo,
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
                        timestamp
                    ))

                    cursor.execute("""
                        INSERT INTO monitoramento (
                                tipo_operacao,
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
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        self.observador.loc.get_text("op_scanned"),
                        nome,
                        "",
                        caminho,
                        metadados.get("data_criacao", ""),
                        metadados.get("data_modificacao", ""),
                        metadados.get("data_acesso", ""),
                        tipo,
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
                        timestamp
                    ))

                    self.contador_processados += 1
                    if self.contador_processados % self.intervalo_atualizacao == 0:
                        self._atualizar_progresso()

                except Exception as e:
                    print(f"Erro ao processar item {nome}: {e}")
                    continue

            conn.commit()

    except Exception as e:
        print(f"Erro ao processar lote: {e}")
        raise
