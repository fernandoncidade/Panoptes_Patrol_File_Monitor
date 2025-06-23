import sqlite3
from datetime import datetime

def registrar_evento_no_banco(self, evento):
    try:
        for campo_obrigatorio in ["tipo_operacao", "nome"]:
            if campo_obrigatorio not in evento:
                print(f"Erro: Campo obrigatório '{campo_obrigatorio}' ausente no evento")
                return

        if "dir_anterior" in evento and (not evento["dir_anterior"] or evento["dir_anterior"] == "."):
            evento["dir_anterior"] = ""

        if "dir_atual" in evento and (not evento["dir_atual"] or evento["dir_atual"] == "."):
            evento["dir_atual"] = ""

        mapeamento_tabelas = {
            self.observador.loc.get_text("op_added"): "adicionado",
            self.observador.loc.get_text("op_deleted"): "excluido",
            self.observador.loc.get_text("op_modified"): "modificado", 
            self.observador.loc.get_text("op_renamed"): "renomeado",
            self.observador.loc.get_text("op_moved"): "movido",
            self.observador.loc.get_text("op_scanned"): "escaneado"
        }

        tipo_operacao_original = evento["tipo_operacao"]
        tabela_especifica = mapeamento_tabelas.get(tipo_operacao_original)

        if not tabela_especifica:
            print(f"Erro: Tipo de operação desconhecido: {tipo_operacao_original}")
            return

        campos_opcionais = [
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
            "tabelas"
        ]

        for campo in campos_opcionais:
            if campo not in evento:
                evento[campo] = ""

        if "timestamp" not in evento:
            evento["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("BEGIN TRANSACTION")

            try:
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

                valores = [evento.get(coluna.replace("tipo_operacao", "tipo_operacao"), "") for coluna in colunas]
                valores[0] = tipo_operacao_original

                placeholders = ", ".join(["?" for _ in colunas])
                colunas_str = ", ".join(colunas)

                query_tabela = f"INSERT INTO {tabela_especifica} ({colunas_str}) VALUES ({placeholders})"
                cursor.execute(query_tabela, valores)

                query_monitoramento = f"INSERT INTO monitoramento ({colunas_str}) VALUES ({placeholders})"
                cursor.execute(query_monitoramento, valores)

                cursor.execute("COMMIT")
                print(f"Evento registrado com sucesso: {tipo_operacao_original} - {evento.get('nome')}")

                self._atualizar_interface_apos_evento(evento)

            except Exception as e:
                cursor.execute("ROLLBACK")
                print(f"Erro durante registro de evento, transação cancelada: {e}")
                raise

    except Exception as e:
        print(f"Erro ao registrar evento no banco: {e}")
