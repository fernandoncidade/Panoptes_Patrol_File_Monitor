from utils.LogManager import LogManager


class ManipuladorTabela:
    @staticmethod
    def configurar_tabela(interface):
        logger = LogManager.get_logger()
        try:
            logger.debug("Configurando tabela de dados")
            if hasattr(interface, 'gerenciador_tabela'):
                interface.gerenciador_tabela.configurar_tabela(interface.tabela_dados)
                logger.debug("Tabela configurada com sucesso")

            else:
                logger.warning("Aviso: gerenciador_tabela não inicializado")

        except Exception as e:
            logger.error(f"Erro ao configurar tabela: {e}", exc_info=True)

    @staticmethod
    def atualizar_visibilidade_colunas(interface):
        logger = LogManager.get_logger()
        try:
            logger.debug("Atualizando visibilidade das colunas")
            if hasattr(interface, 'gerenciador_tabela'):
                interface.gerenciador_tabela.configurar_tabela(interface.tabela_dados)
                interface.atualizar_status()
                logger.info("Visibilidade das colunas atualizada com sucesso")

            else:
                logger.warning("gerenciador_tabela não está disponível para atualizar visibilidade das colunas")

        except Exception as e:
            logger.error(f"Erro ao atualizar visibilidade das colunas: {e}", exc_info=True)
