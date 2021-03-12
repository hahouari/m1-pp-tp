#!/usr/bin/python3

from pp import lexical_analysis, syntax_analysis, terms_separator, terms_table
from PyQt5.QtGui import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QMargins

import sys


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Master 1 - Paradigmes de Programmation - TP1")

        g_layout = QVBoxLayout()
        terms_layout = QHBoxLayout()

        term_label = QLabel("Inserer les termes:", self)

        self.terms_input = QLineEdit(self)
        self.terms_input.textEdited.connect(self.on_validate)

        table_label = QLabel("Table des termes classifiées:", self)
        self.terms_table_holder = QPlainTextEdit()
        self.terms_table_holder.setReadOnly(True)

        terms_layout.addWidget(self.terms_input)
        terms_layout.setContentsMargins(QMargins())

        terms_widget = QWidget()
        terms_widget.setLayout(terms_layout)

        g_layout.addWidget(term_label)
        g_layout.addWidget(terms_widget)

        g_layout.addWidget(table_label)
        g_layout.addWidget(self.terms_table_holder)

        widget = QWidget()
        widget.setLayout(g_layout)

        self.setCentralWidget(widget)

    def on_validate(self):
        terms_text = lexical_analysis(self.terms_input.text())
        terms_list = terms_separator(terms_text)
        terms_list = syntax_analysis(terms_list)
        self.terms_table_holder.setPlainText(terms_table(terms_list))


app = QApplication(sys.argv)
window = MainWindow()
window.resize(500, 380)
window.move(80, 100)
window.show()

app.exec_()
