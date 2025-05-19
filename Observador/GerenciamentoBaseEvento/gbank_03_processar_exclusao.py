import sqlite3
from datetime import datetime

def processar_exclusao(self, evento):
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            query = """
                SELECT 
                    m.tipo_operacao,
                    m.nome,
                    m.dir_anterior,
                    m.dir_atual,
                    m.data_criacao,
                    m.data_modificacao,
                    m.data_acesso,
                    m.tipo,
                    m.tamanho,
                    m.atributos,
                    m.autor,
                    m.dimensoes,
                    m.duracao, 
                    m.taxa_bits,
                    m.protegido,
                    m.paginas,
                    m.linhas,
                    m.palavras,
                    m.paginas_estimadas,
                    m.linhas_codigo,
                    m.total_linhas,
                    m.slides_estimados,
                    m.arquivos,
                    m.descompactados,
                    m.slides,
                    m.binario,
                    m.planilhas,
                    m.colunas,
                    m.registros,
                    m.tabelas,
                    m.timestamp
                FROM monitoramento m
                WHERE m.nome = ?

                UNION ALL

                SELECT 
                    NULL as tipo_operacao,
                    s.nome,
                    s.diretorio as dir_anterior,
                    s.diretorio as dir_atual,
                    s.data_criacao,
                    s.data_modificacao,
                    s.data_acesso,
                    s.tipo,
                    s.tamanho,
                    s.atributos,
                    s.autor,
                    s.dimensoes,
                    s.duracao, 
                    s.taxa_bits,
                    s.protegido,
                    s.paginas,
                    s.linhas,
                    s.palavras,
                    s.paginas_estimadas,
                    s.linhas_codigo,
                    s.total_linhas,
                    s.slides_estimados,
                    s.arquivos,
                    s.descompactados,
                    s.slides,
                    s.binario,
                    s.planilhas,
                    s.colunas,
                    s.registros,
                    s.tabelas,
                    s.timestamp
                FROM snapshot s
                WHERE s.nome = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """

            cursor.execute(query, (evento.get("nome"), evento.get("nome")))
            result = cursor.fetchone()

            colunas = [
                "tipo_operacao",
                "nome",
                "dir_anterior",
                "dir_atual",
                "data_criacao",
                "data_modificacao",
                "data_acesso",
                "tipo",
                "tamanho",
                "atributos",
                "autor",
                "dimensoes",
                "duracao", 
                "taxa_bits",
                "protegido",
                "paginas",
                "linhas",
                "palavras",
                "paginas_estimadas",
                "linhas_codigo",
                "total_linhas",
                "slides_estimados",
                "arquivos",
                "descompactados",
                "slides",
                "binario",
                "planilhas",
                "colunas",
                "registros",
                "tabelas",
                "timestamp"
            ]
            print(f"Processando exclusão para: {evento.get('nome')}")

            if result:
                metadados = dict(zip(colunas, result))
                print(f"Metadados encontrados: tipo={metadados.get('tipo')}, dir={metadados.get('dir_anterior')}")

            else:
                metadados = {
                    "nome": evento.get("nome"),
                    "dir_anterior": evento.get("dir_anterior"),
                    "dir_atual": "",
                    "tipo": self.observador.gerenciador_colunas.identificar_tipo_arquivo(evento.get("nome")),
                    "data_criacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data_modificacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data_acesso": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tamanho": "",
                    "atributos": "",
                    "autor": "",
                    "dimensoes": "",
                    "duracao": "",
                    "taxa_bits": "",
                    "protegido": "",
                    "paginas": "",
                    "linhas": "",
                    "palavras": "",
                    "paginas_estimadas": "",
                    "linhas_codigo": "",
                    "total_linhas": "",
                    "slides_estimados": "",
                    "arquivos": "",
                    "descompactados": "",
                    "slides": "",
                    "binario": "",
                    "planilhas": "",
                    "colunas": "",
                    "registros": "",
                    "tabelas": ""
                }
                print(f"Nenhum metadado encontrado, usando valores default. Tipo identificado: {metadados['tipo']}")

            valores = (
                self.observador.loc.get_text("op_deleted"),
                metadados.get("nome"),
                evento.get("dir_anterior"),
                "",
                metadados.get("data_criacao"),
                metadados.get("data_modificacao"),
                metadados.get("data_acesso"),
                metadados.get("tipo"),
                metadados.get("tamanho"),
                metadados.get("atributos"),
                metadados.get("autor"),
                metadados.get("dimensoes"),
                metadados.get("duracao"),
                metadados.get("taxa_bits"),
                metadados.get("protegido"),
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
            )
            cursor.execute("BEGIN TRANSACTION")

            cursor.execute("""
                INSERT INTO excluido (
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
            """, valores)

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
            """, valores)

            cursor.execute("COMMIT")
            print(f"Registro de exclusão concluído para: {evento.get('nome')}")

            if not evento.get("_temporario", False):
                self._atualizar_interface_apos_exclusao()

    except Exception as e:
        print(f"Erro ao processar exclusão: {e}")
        try:
            if conn:
                cursor.execute("ROLLBACK")

        except Exception:
            pass
