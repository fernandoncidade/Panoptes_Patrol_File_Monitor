import os
from PySide6.QtGui import QIcon, QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton


class GerenciadorBotoesUI:
    def __init__(self, parent):
        self.parent = parent
        self.buttons_data = []

    def add_button_with_label(self, layout, label_text, icon_name, callback, icon_path, translation_key=None):
        layout_h = QHBoxLayout()
        label = QLabel(label_text, self.parent)
        layout_h.addWidget(label)

        button = self.create_button()
        button.setIcon(QIcon(os.path.join(icon_path, icon_name)))
        button.clicked.connect(callback)
        layout_h.addWidget(button)
        layout.addLayout(layout_h)

        if translation_key is None:
            translation_key = label_text

        self.buttons_data.append({'label': label, 'translation_key': translation_key})
        return button

    def update_buttons_text(self, loc):
        for entry in self.buttons_data:
            entry['label'].setText(loc.get_text(entry['translation_key']))

    def create_button(self):
        button = QPushButton()
        button.setMinimumWidth(3 * button.fontMetrics().horizontalAdvance('m'))
        button.setMaximumWidth(3 * button.fontMetrics().horizontalAdvance('m'))
        button.setFont(QFont('Arial', 9))
        return button
