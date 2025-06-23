from utils.LogManager import LogManager
from PySide6.QtCore import QLocale, QLibraryInfo, QTranslator
from PySide6.QtWidgets import QApplication


class Internacionalizador:
    @staticmethod
    def atualizar_tradutor_qt(interface, idioma):
        logger = LogManager.get_logger()

        try:
            logger.info(f"Atualizando traduções do Qt para {idioma}")

            for translator in QApplication.instance().findChildren(QTranslator):
                QApplication.instance().removeTranslator(translator)

            qt_translator = QTranslator(QApplication.instance())
            translations_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
            locale = QLocale(idioma)

            success = qt_translator.load(locale, 'qtbase', '_', translations_path)
            QApplication.instance().installTranslator(qt_translator)

            logger.info(f"Traduções do Qt atualizadas para {idioma}: {'sucesso' if success else 'falha'}")

        except Exception as e:
            logger.error(f"Erro ao atualizar tradutor Qt: {e}", exc_info=True)

    @staticmethod
    def inicializar_tradutor_qt(app, idioma):
        logger = LogManager.get_logger()

        try:
            logger.info(f"Inicializando traduções do Qt para {idioma}")

            qt_translator = QTranslator(app)
            translations_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
            locale = QLocale(idioma)

            success = qt_translator.load(locale, 'qtbase', '_', translations_path)
            app.installTranslator(qt_translator)

            logger.info(f"Traduções do Qt carregadas para o idioma {idioma}: {'sucesso' if success else 'falha'}")
            return qt_translator

        except Exception as e:
            logger.error(f"Erro ao inicializar tradutor Qt: {e}", exc_info=True)
            return None
