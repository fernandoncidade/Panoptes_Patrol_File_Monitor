import os

def extrair_metadados_banco_dados(caminho, loc):
    metadados = {}
    ext = os.path.splitext(caminho)[1].lower()

    try:
        if ext == '.sqlite' or ext == '.db':
            try:
                import sqlite3
                conexao = sqlite3.connect(caminho)
                cursor = conexao.cursor()

                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tabelas = cursor.fetchall()

                num_tabelas = len(tabelas)
                nomes_tabelas = ", ".join([t[0] for t in tabelas if t[0] != 'sqlite_sequence'])

                metadados['tabelas'] = num_tabelas
                metadados['nomes_tabelas'] = nomes_tabelas

                total_linhas = 0
                for tabela in tabelas[:5]:
                    nome_tabela = tabela[0]
                    if nome_tabela != 'sqlite_sequence':
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM '{nome_tabela}';")
                            contagem = cursor.fetchone()[0]
                            total_linhas += contagem

                        except:
                            pass

                metadados['linhas_estimadas'] = total_linhas
                metadados['registros'] = str(total_linhas)  
                metadados['linhas'] = str(total_linhas)

                conexao.close()

            except Exception as e:
                print(f"Erro ao extrair metadados do banco SQLite {caminho}: {e}")

        elif ext == '.mdb' or ext == '.accdb':
            try:
                import pyodbc
                conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};' fr'DBQ={caminho};')
                conn = pyodbc.connect(conn_str)
                cursor = conn.cursor()

                tabelas = []
                for tabela in cursor.tables(tableType='TABLE'):
                    tabelas.append(tabela.table_name)

                metadados['tabelas'] = len(tabelas)
                metadados['nomes_tabelas'] = ", ".join(tabelas[:10])

                conn.close()

            except Exception as e:
                print(f"Erro ao extrair metadados do Access {caminho}: {e}")
                metadados['tipo_acesso'] = "Microsoft Access Database"

    except Exception as e:
        print(f"Erro geral ao extrair metadados do banco de dados {caminho}: {e}")

    return metadados
