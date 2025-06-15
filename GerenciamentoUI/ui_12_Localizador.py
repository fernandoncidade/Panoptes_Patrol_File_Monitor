import os
import sys
import json
import locale
from PySide6.QtCore import QObject, Signal

def obter_caminho_persistente():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)

    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_dir = os.path.join(base_path, "config")

    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)

        except Exception as e:
            print(f"Erro ao criar diretório de configuração: {e}")

    return config_dir

from GerenciamentoUI.Localizacoes import todas_traducoes
from GerenciamentoUI.Localizacoes.tr_07_TradutorMetadados import traduzir_tipo_operacao, traduzir_metadados


class Localizador(QObject):
    idioma_alterado = Signal(str)

    def set_idioma(self, idioma: str):
        if idioma in self.traducoes:
            self.idioma_atual = idioma
            self.salvar_preferencia_idioma(idioma)
            self.idioma_alterado.emit(idioma)

    def salvar_preferencia_idioma(self, idioma: str):
        try:
            config_path = os.path.join(obter_caminho_persistente(), "language_config.json")
            with open(config_path, 'w') as f:
                json.dump({"idioma": idioma}, f)

            print(f"Preferência de idioma salva em: {config_path}")

        except Exception as e:
            print(f"Erro ao salvar preferência de idioma: {e}")

    def carregar_preferencia_idioma(self):
        try:
            config_path = os.path.join(obter_caminho_persistente(), "language_config.json")

            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get("idioma", self.system_locale)

            else:
                with open(config_path, 'w') as f:
                    json.dump({"idioma": self.system_locale}, f)

                print(f"Arquivo de configuração de idioma criado em: {config_path}")
                return self.system_locale

        except Exception as e:
            print(f"Erro ao carregar/criar preferência de idioma: {e}")
            return self.system_locale

    def __init__(self):
        super().__init__()
        self.system_locale = locale.getdefaultlocale()[0]
        self.idioma_atual = self.carregar_preferencia_idioma()
        self.traducoes = todas_traducoes

    def verificar_traducoes_ausentes(self):
        todas_chaves = set()
        for traducoes in self.traducoes.values():
            todas_chaves.update(traducoes.keys())

        for idioma, traducoes in self.traducoes.items():
            ausentes = todas_chaves - set(traducoes.keys())
            if ausentes:
                print(f"Traduções ausentes para {idioma}:")
                for chave in sorted(ausentes):
                    print(f"  - {chave}")

    def get_text(self, key: str) -> str:
        try:
            return self.traducoes.get(self.idioma_atual, {}).get(key, key)

        except:
            return key

    def get_idiomas_disponiveis(self):
        if self.idioma_atual == "pt_BR":
            return {
                "pt_BR": "Português Brasileiro | Brazilian Portuguese",
                "en_US": "Inglês (EUA) | English (US)",
                "es_ES": "Espanhol | Español",
                "fr_FR": "Francês | Français",
                "it_IT": "Italiano | Italiano",
                "de_DE": "Alemão | Deutsch"
            }

        elif self.idioma_atual == "en_US":
            return {
                "pt_BR": "Brazilian Portuguese | Português Brasileiro",
                "en_US": "English (US) | Inglês (US)",
                "es_ES": "Spanish | Español",
                "fr_FR": "French | Français",
                "it_IT": "Italian | Italiano",
                "de_DE": "German | Deutsch"
            }

        elif self.idioma_atual == "es_ES":
            return {
                "pt_BR": "Portugués Brasileño | Português Brasileiro",
                "en_US": "Inglés (EEUU) | English (US)",
                "es_ES": "Español | Spanish",
                "fr_FR": "Francés | Français",
                "it_IT": "Italiano | Italiano",
                "de_DE": "Alemán | Deutsch"
            }

        elif self.idioma_atual == "fr_FR":
            return {
                "pt_BR": "Portugais Brésilien | Português Brasileiro",
                "en_US": "Anglais (États-Unis) | English (US)",
                "es_ES": "Espagnol | Español",
                "fr_FR": "Français | French",
                "it_IT": "Italien | Italiano",
                "de_DE": "Allemand | Deutsch"
            }

        elif self.idioma_atual == "it_IT":
            return {
                "pt_BR": "Portoghese Brasiliano | Português Brasileiro",
                "en_US": "Inglese (Stati Uniti) | English (US)",
                "es_ES": "Spagnolo | Español",
                "fr_FR": "Francese | Français",
                "it_IT": "Italiano | Italian",
                "de_DE": "Tedesco | Deutsch"
            }

        elif self.idioma_atual == "de_DE":
            return {
                "pt_BR": "Brasilianisches Portugiesisch | Português Brasileiro",
                "en_US": "Englisch (USA) | English (US)",
                "es_ES": "Spanisch | Español",
                "fr_FR": "Französisch | Français",
                "it_IT": "Italienisch | Italiano",
                "de_DE": "Deutsch | German"
            }

        else:
            return {
                "pt_BR": "Brazilian Portuguese | Português Brasileiro",
                "en_US": "English (US) | Inglês (US)",
                "es_ES": "Spanish | Español",
                "fr_FR": "French | Français",
                "it_IT": "Italian | Italiano",
                "de_DE": "German | Deutsch"
            }

    def traduzir_tipo_operacao(self, valor, idioma_origem=None):
        return traduzir_tipo_operacao(self, valor, idioma_origem)

    def traduzir_metadados(self, valor, campo):
        return traduzir_metadados(self, valor, campo)
