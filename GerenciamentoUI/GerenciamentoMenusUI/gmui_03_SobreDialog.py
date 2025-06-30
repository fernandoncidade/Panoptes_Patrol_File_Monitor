from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextBrowser, QSizePolicy, QHBoxLayout
from PySide6.QtCore import Qt


class SobreDialog(QDialog):
    def __init__(self, parent, titulo, cabecalho, detalhes, licencas, sites_licencas, show_details_text, hide_details_text, 
                 show_licenses_text, hide_licenses_text, ok_text, site_oficial_text, avisos=None, show_notices_text=None, 
                 hide_notices_text=None, Privacy_Policy=None, show_privacy_policy_text=None, hide_privacy_policy_text=None, 
                 info_not_available_text="Information not available"):
        super().__init__(parent)
        self.setWindowTitle(titulo)

        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)

        layout = QVBoxLayout(self)

        self.header_label = QLabel(cabecalho)
        self.header_label.setTextFormat(Qt.TextFormat.RichText)
        self.header_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.header_label)

        button_layout = QHBoxLayout()

        self.details_button = QPushButton(show_details_text)
        self.details_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.details_button.clicked.connect(self.toggle_details)
        button_layout.addWidget(self.details_button)

        self.licenses_button = QPushButton(show_licenses_text)
        self.licenses_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.licenses_button.clicked.connect(self.toggle_licenses)
        button_layout.addWidget(self.licenses_button)

        self.notices_button = QPushButton(show_notices_text)
        self.notices_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.notices_button.clicked.connect(self.toggle_notices)
        button_layout.addWidget(self.notices_button)

        self.privacy_policy_button = QPushButton(show_privacy_policy_text)
        self.privacy_policy_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.privacy_policy_button.clicked.connect(self.toggle_privacy_policy)
        button_layout.addWidget(self.privacy_policy_button)

        self.ok_button = QPushButton(ok_text)
        self.ok_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)

        button_layout.addStretch(1)

        layout.addLayout(button_layout)

        self.details_edit = QTextBrowser()
        self.details_edit.setReadOnly(True)
        self.details_edit.setVisible(False)
        self.details_edit.setOpenExternalLinks(True)
        layout.addWidget(self.details_edit, 1)

        self.show_details_text = show_details_text
        self.hide_details_text = hide_details_text
        self.show_licenses_text = show_licenses_text
        self.hide_licenses_text = hide_licenses_text
        self.show_notices_text = show_notices_text
        self.hide_notices_text = hide_notices_text
        self.show_privacy_policy_text = show_privacy_policy_text
        self.hide_privacy_policy_text = hide_privacy_policy_text
        self.site_oficial_text = site_oficial_text
        self.info_not_available_text = info_not_available_text

        self.detalhes = detalhes
        self.licencas = licencas
        self.sites_licencas = sites_licencas
        self.avisos = avisos
        self.Privacy_Policy = Privacy_Policy

        self.showing_details = False
        self.showing_licenses = False
        self.showing_notices = False
        self.showing_privacy_policy = False

        self.setMinimumSize(500, 300)

    def toggle_details(self):
        if self.showing_licenses:
            self.showing_licenses = False
            self.licenses_button.setText(self.show_licenses_text)

        if self.showing_notices:
            self.showing_notices = False
            self.notices_button.setText(self.show_notices_text)

        if hasattr(self, 'showing_privacy_policy') and self.showing_privacy_policy:
            self.showing_privacy_policy = False
            self.privacy_policy_button.setText(self.show_privacy_policy_text)

        self.showing_details = not self.showing_details
        self.details_edit.setVisible(self.showing_details)

        if self.showing_details:
            self.details_button.setText(self.hide_details_text)
            self.details_edit.setPlainText(self.detalhes)

        else:
            self.details_button.setText(self.show_details_text)

        self._adjust_dialog_size()

    def toggle_licenses(self):
        if self.showing_details:
            self.showing_details = False
            self.details_button.setText(self.show_details_text)

        if self.showing_notices:
            self.showing_notices = False
            self.notices_button.setText(self.show_notices_text)

        if hasattr(self, 'showing_privacy_policy') and self.showing_privacy_policy:
            self.showing_privacy_policy = False
            self.privacy_policy_button.setText(self.show_privacy_policy_text)

        self.showing_licenses = not self.showing_licenses
        self.details_edit.setVisible(self.showing_licenses)

        if self.showing_licenses:
            self.licenses_button.setText(self.hide_licenses_text)

            texto_html = self.licencas.replace('\n', '<br>')

            texto_html += f"<br><br><h3>{self.site_oficial_text}</h3><ul>"
            for site in self.sites_licencas.strip().split('\n'):
                if site.strip():
                    texto_html += f'<li><a href="{site.strip()}">{site.strip()}</a></li>'

            texto_html += "</ul>"

            self.details_edit.setHtml(texto_html)

        else:
            self.licenses_button.setText(self.show_licenses_text)
            self.details_edit.clear()

        self._adjust_dialog_size()

    def toggle_notices(self):
        if self.showing_details:
            self.showing_details = False
            self.details_button.setText(self.show_details_text)

        if self.showing_licenses:
            self.showing_licenses = False
            self.licenses_button.setText(self.show_licenses_text)

        if hasattr(self, 'showing_privacy_policy') and self.showing_privacy_policy:
            self.showing_privacy_policy = False
            self.privacy_policy_button.setText(self.show_privacy_policy_text)

        self.showing_notices = not self.showing_notices
        self.details_edit.setVisible(self.showing_notices)

        if self.showing_notices:
            self.notices_button.setText(self.hide_notices_text)

            if self.avisos:
                self.details_edit.setHtml(self.avisos.replace('\n', '<br>'))

            else:
                self.details_edit.setHtml(f"<p>{self.info_not_available_text}.</p>")

        else:
            self.notices_button.setText(self.show_notices_text)
            self.details_edit.clear()

        self._adjust_dialog_size()

    def toggle_privacy_policy(self):
        if self.showing_details:
            self.showing_details = False
            self.details_button.setText(self.show_details_text)

        if self.showing_licenses:
            self.showing_licenses = False
            self.licenses_button.setText(self.show_licenses_text)

        if self.showing_notices:
            self.showing_notices = False
            self.notices_button.setText(self.show_notices_text)

        self.showing_privacy_policy = not getattr(self, 'showing_privacy_policy', False)
        self.details_edit.setVisible(self.showing_privacy_policy)

        if self.showing_privacy_policy:
            self.privacy_policy_button.setText(self.hide_privacy_policy_text)

            if self.Privacy_Policy:
                self.details_edit.setHtml(self.Privacy_Policy.replace('\n', '<br>'))

            else:
                self.details_edit.setHtml(f"<p>{self.info_not_available_text}.</p>")

        else:
            self.privacy_policy_button.setText(self.show_privacy_policy_text)
            self.details_edit.clear()

        self._adjust_dialog_size()

    def _adjust_dialog_size(self):
        if self.showing_details or self.showing_licenses or self.showing_notices:
            current_size = self.size()
            if current_size.height() < 450:
                self.resize(current_size.width(), 450)
