import sqlite3

def obter_metadados_arquivo_excluido(self, nome):
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT 
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
                FROM monitoramento
                WHERE nome = ?
                ORDER BY id DESC
                LIMIT 1
            """, (nome,))

            resultado = cursor.fetchone()
            if resultado:
                colunas = ['tipo_operacao', 
                            'nome', 
                            'dir_anterior', 
                            'dir_atual', 
                            'data_criacao', 
                            'data_modificacao', 
                            'data_acesso', 
                            'tipo', 
                            'tamanho', 
                            'atributos', 
                            'autor', 
                            'dimensoes', 
                            'duracao', 
                            'taxa_bits', 
                            'protegido', 
                            'paginas',
                            'linhas',
                            'palavras',
                            'paginas_estimadas',
                            'linhas_codigo',
                            'total_linhas',
                            'slides_estimados',
                            'arquivos',
                            'descompactados',
                            'slides',
                            'binario',
                            'planilhas',
                            'colunas',
                            'registros',
                            'tabelas',
                            'timestamp']
                return dict(zip(colunas, resultado))

            cursor.execute("""
                SELECT NULL as 
                        tipo_operacao, 
                        nome, 
                        diretorio as dir_anterior, 
                        diretorio as dir_atual, 
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
                FROM snapshot
                WHERE nome = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (nome,))

            resultado = cursor.fetchone()
            if resultado:
                colunas = ['tipo_operacao', 
                        'nome', 
                        'dir_anterior', 
                        'dir_atual', 
                        'data_criacao', 
                        'data_modificacao', 
                        'data_acesso',
                        'tipo', 
                        'tamanho', 
                        'atributos', 
                        'autor', 
                        'dimensoes', 
                        'duracao', 
                        'taxa_bits', 
                        'protegido', 
                        'paginas',
                        'linhas',
                        'palavras',
                        'paginas_estimadas',
                        'linhas_codigo',
                        'total_linhas',
                        'slides_estimados',
                        'arquivos',
                        'descompactados',
                        'slides',
                        'binario',
                        'planilhas',
                        'colunas',
                        'registros',
                        'tabelas',
                        'timestamp']
                return dict(zip(colunas, resultado))

            return None

    except Exception as e:
        print(f"Erro ao buscar metadados de arquivo excluído: {e}")
        return None
