from datetime import datetime

def _inserir_evento_movido(self, cursor, evento):
    if not evento or evento.get("tipo_operacao") != self.observador.loc.get_text("op_moved"):
        return False

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

        valores = []
        for coluna in colunas:
            if coluna == "tipo_operacao":
                valores.append(self.observador.loc.get_text("op_moved"))

            elif coluna == "timestamp" and "timestamp" not in evento:
                valores.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            else:
                valores.append(evento.get(coluna, ""))

        placeholders = ", ".join(["?" for _ in colunas])
        colunas_str = ", ".join(colunas)

        cursor.execute(f"INSERT INTO movido ({colunas_str}) VALUES ({placeholders})", valores)
        cursor.execute(f"INSERT INTO monitoramento ({colunas_str}) VALUES ({placeholders})", valores)

        return True

    except Exception as e:
        print(f"Erro ao inserir evento movido: {e}")
        return False
