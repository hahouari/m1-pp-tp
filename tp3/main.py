#!/bin/python3

from pp import terms_table, unification_engine, lexical_analysis, syntax_analysis, terms_separator
from PyQt5.QtGui import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QMargins

import sys


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Master 1 - Paradigmes de Programmation - TP 3")

        g_layout = QHBoxLayout()
        l_layout = QVBoxLayout()
        l_layout.setContentsMargins(QMargins(0, 0, 4, 0))
        self.ops_layout = QVBoxLayout()
        self.ops_layout.setContentsMargins(QMargins())
        r_layout = QVBoxLayout()
        r_layout.setContentsMargins(QMargins())

        ops_label = QLabel("Inserer les deux termes:", self)
        l_layout.addWidget(ops_label)

        self.ops_left_inputs = []
        self.ops_right_inputs = []
        self.drop_btns = []

        ops_widget = QWidget(self)
        ops_widget.setLayout(self.ops_layout)
        l_layout.addWidget(ops_widget)

        self.insert_new_op()

        table_label = QLabel("La table des termes classifiées:", self)

        self.add_btn = QPushButton(
            QIcon('./icons/plus.png'),
            ' &Add',
            self
        )
        self.add_btn.setFixedWidth(60)
        self.add_btn.clicked.connect(lambda _: self.insert_new_op(True))

        self.validate_btn = QPushButton(
            QIcon('./icons/validate.png'),
            ' &Valider',
            self
        )
        self.validate_btn.setFixedWidth(80)
        self.validate_btn.clicked.connect(self.on_validate)

        self.terms_table_holder = QPlainTextEdit()
        self.terms_table_holder.setReadOnly(True)

        valid_layout = QHBoxLayout()
        valid_layout.setContentsMargins(QMargins())
        valid_layout.addWidget(table_label)
        valid_layout.addWidget(self.add_btn)
        valid_layout.addWidget(self.validate_btn)

        valid_widget = QWidget(self)
        valid_widget.setLayout(valid_layout)
        l_layout.addWidget(valid_widget)

        l_layout.addWidget(self.terms_table_holder)

        l_widget = QWidget(self)
        l_widget.setLayout(l_layout)

        unification_label = QLabel("La table de l'unification:", self)
        self.unification_holder = QPlainTextEdit()
        self.unification_holder.setReadOnly(True)

        r_layout.addWidget(unification_label)
        r_layout.addWidget(self.unification_holder)

        r_widget = QWidget(self)
        r_widget.setLayout(r_layout)

        g_layout.addWidget(l_widget)
        g_layout.addWidget(r_widget)

        g_widget = QWidget(self)
        g_widget.setLayout(g_layout)

        self.setCentralWidget(g_widget)

    def insert_new_op(self, dropable=False):
        self.ops_left_inputs.append(QLineEdit(self))
        self.ops_right_inputs.append(QLineEdit(self))

        self.drop_btns.append(QPushButton(
            QIcon('./icons/cancel.png'),
            '',
            self
        ))
        self.drop_btns[-1].setDisabled(not dropable)
        self.drop_btns[-1].setFixedWidth(24)

        op_layout = QHBoxLayout()
        op_layout.setContentsMargins(QMargins())
        op_layout.addWidget(self.ops_left_inputs[-1])
        op_layout.addWidget(QLabel("=", self))
        op_layout.addWidget(self.ops_right_inputs[-1])
        op_layout.addWidget(self.drop_btns[-1])

        op_widget = QWidget(self)
        op_widget.setLayout(op_layout)
        self.ops_layout.addWidget(op_widget)

        if dropable:
            self.drop_btns[-1].clicked.connect(
                lambda _: self.remove_op(op_widget, len(self.drop_btns)-1)
            )

    def remove_op(self, op_widget: QWidget, index):
        op_layout = op_widget.layout()

        for i in reversed(range(op_layout.count())):
            op_layout.itemAt(i).widget().setParent(None)

        self.ops_layout.removeWidget(op_widget)
        op_widget.setParent(None)
        self.ops_left_inputs.pop(index)
        self.ops_right_inputs.pop(index)

    def on_validate(self):
        ops_left = []
        ops_right = []
        self.terms_table_holder.setPlainText('')

        for left_input, right_input in zip(self.ops_left_inputs, self.ops_right_inputs):
            if not left_input.text() or not right_input.text():
                continue
            lexical_left = lexical_analysis(left_input.text())
            lexical_right = lexical_analysis(right_input.text())
            ops_left.append(terms_separator(lexical_left))
            ops_right.append(terms_separator(lexical_right))
            ops_left[-1] = syntax_analysis(ops_left[-1])[0]
            ops_right[-1] = syntax_analysis(ops_right[-1])[0]

            self.terms_table_holder.insertPlainText(
                '---------------------------------------------------\n'
                '1er terme: ----------\n' +
                (terms_table(ops_left[-1]) or '<Pas des termes>\n') +
                '2eme terme: ----------\n' +
                (terms_table(ops_right[-1]) or '<Pas des termes>\n')
            )

        self.unification_holder.setPlainText(
            unification_engine(ops_left, ops_right)
        )


app = QApplication(sys.argv)
window = MainWindow()
window.resize(750, 500)
window.move(80, 100)
window.show()

app.exec_()
