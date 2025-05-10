import logging
from Observador.ob_08_EventoMovido import _atualizar_contador_eventos


class GerenciadorMensagens:
    @staticmethod
    def atualizar_rotulos(interface):
        logger = logging.getLogger('FileManager')
        try:
            logger.debug("Atualizando rótulos da interface")

            if interface.diretorio_atual:
                interface.rotulo_diretorio.setText(interface.loc.get_text("dir_selected").format(interface.diretorio_atual))

            else:
                interface.rotulo_diretorio.setText(interface.loc.get_text("no_dir"))

            if interface.observador and interface.observador.ativo:
                interface.rotulo_resultado.setText(interface.loc.get_text("monitoring_started"))

            elif interface.observador and not interface.observador.ativo:
                interface.rotulo_resultado.setText(interface.loc.get_text("monitoring_stopped"))

            else:
                interface.rotulo_resultado.setText(interface.loc.get_text("select_to_start"))

            _atualizar_contador_eventos(interface)

            logger.debug("Rótulos atualizados com sucesso")

        except Exception as e:
            logger.error(f"Erro ao atualizar rótulos: {e}")

    @staticmethod
    def notificar_erro(interface, mensagem):
        logger = logging.getLogger('FileManager')
        try:
            logger.error(f"Notificando erro: {mensagem}")
            interface.rotulo_resultado.setText(f"Erro: {mensagem}")

        except Exception as e:
            logger.error(f"Erro ao notificar erro: {e}")

    @staticmethod
    def notificar_sucesso(interface, mensagem):
        logger = logging.getLogger('FileManager')
        try:
            logger.info(f"Notificando sucesso: {mensagem}")
            interface.rotulo_resultado.setText(mensagem)

        except Exception as e:
            logger.error(f"Erro ao notificar sucesso: {e}")
