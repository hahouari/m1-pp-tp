#!/bin/python3

from PyQt5.QtGui import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QMargins

import sys
import re

# regex dict definition, used by regex to produce global regex, and syntax_analysis
REGEX_DICT = {}
REGEX_DICT['FUNCTION'] = r"[a-zA-Z][\w_]*\(\)?"
REGEX_DICT['PARENTHESES_CLOSE'] = r"\)"
REGEX_DICT['VARIABLE'] = r"[a-zA-Z][\w_]*"
REGEX_DICT['CONST'] = r"\-?(\.\d+|\d+(\.\d*)?)|\"[^\"]*\""
REGEX_DICT['COMMA'] = r","
REGEX_DICT['PARENTHESES_OPEN'] = r"\("
REGEX_DICT['SPACE'] = r"[ ]+"

regex = r"\"[^\"]*\"|[-+]?[\w_\.]+(\(\)?)?|\)|,|[ ]+"


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Master 1 - Paradigmes de Programmation")

        g_layout = QVBoxLayout()

        funs_label = QLabel("Inserer les deux fonctions:", self)

        self.fun1_input = QLineEdit(self)
        self.validate_btn = QPushButton(
            QIcon('./validate.png'),
            ' &Valider',
            self
        )
        self.validate_btn.setFixedWidth(80)
        self.validate_btn.clicked.connect(self.on_validate)

        self.fun2_input = QLineEdit(self)

        table_label = QLabel("L'unification:", self)
        self.terms_table_holder = QPlainTextEdit()
        self.terms_table_holder.setReadOnly(True)

        up_layout = QHBoxLayout()
        up_layout.setContentsMargins(QMargins())
        up_layout.addWidget(funs_label)
        up_layout.addWidget(self.validate_btn)

        up_widget = QWidget(self)
        up_widget.setLayout(up_layout)
        g_layout.addWidget(up_widget)

        funs_layout = QHBoxLayout()
        funs_layout.setContentsMargins(QMargins())
        funs_layout.addWidget(self.fun1_input)
        funs_layout.addWidget(QLabel("=", self))
        funs_layout.addWidget(self.fun2_input)

        funs_widget = QWidget(self)
        funs_widget.setLayout(funs_layout)
        g_layout.addWidget(funs_widget)

        g_layout.addWidget(table_label)
        g_layout.addWidget(self.terms_table_holder)

        widget = QWidget()
        widget.setLayout(g_layout)

        self.setCentralWidget(widget)

    def on_validate(self):
        lexical_1 = self.lexical_analysis(self.fun1_input.text())
        lexical_2 = self.lexical_analysis(self.fun2_input.text())
        terms_list1 = self.terms_separator(lexical_1)
        print(terms_list1)
        terms_list2 = self.terms_separator(lexical_2)
        terms_list1 = self.syntax_analysis(terms_list1)
        terms_list2 = self.syntax_analysis(terms_list2)
        # self.terms_table_holder.setPlainText('')
        self.terms_table_holder.setPlainText(
            self.terms_table(terms_list1 + terms_list2)
        )

    def terms_table(self, defined_terms):
        if not len(defined_terms):
            return ''
        terms_str = ""
        terms_str += "{}: {}\n".format(defined_terms[0]['match'][:-2] if re.match(
            "^{}$".format(REGEX_DICT['FUNCTION'][:-1]),
            defined_terms[0]['match']
        ) else defined_terms[0]['match'][:-1] if re.match(
            "^{}$".format(REGEX_DICT['FUNCTION']),
            defined_terms[0]['match']
        ) else defined_terms[0]['match'], defined_terms[0]['message'])
        if defined_terms[0]['message'] == 'Fonction':
            terms_str += self.terms_table(defined_terms[0]['terms'])
        return terms_str + self.terms_table(defined_terms[1:])

    def lexical_analysis(self, input_text):
        return re.sub(regex, lambda amatch: "{}#".format(amatch.group()), input_text)

    def terms_separator(self, terms_text: str):
        terms_list = terms_text.split("#")
        if len(terms_list) and terms_list[-1] == "":
            terms_list.pop()
        return terms_list

    def term_as_dict(self, match, message, error=False):
        the_dict = {
            "match": match,
            "message": message,
            "error": error
        }

        if message == 'Fonction':
            the_dict['terms'] = []

        return the_dict

    def syntax_analysis(self, separated_terms: list):
        defined_terms = []
        append_to = [defined_terms]
        while len(separated_terms):
            term = separated_terms[0]
            # functions need a queue to know if its closed parenthese
            if re.match("^({})$".format(REGEX_DICT['FUNCTION']), term):
                if term[-1] == ')':
                    print('gggggggggggggggggggggggggggggggg')
                    return [self.term_as_dict(
                        term, 'Erreur, Fonction sans des paramètres', True
                    )]
                function_term = self.term_as_dict(term, 'Fonction')
                append_to[-1].append(function_term)
                append_to.append(function_term['terms'])
            # elif re.match("^({})$".format(REGEX_DICT['PARENTHESES_OPEN']), term):
                # open_parentheses_term = self.term_as_dict(term, '')
                # append_to.append(open_parentheses_term)
            elif re.match("^({})$".format(REGEX_DICT['VARIABLE']), term):
                append_to[-1].append(self.term_as_dict(term, 'Variable'))
            elif re.match("^({})$".format(REGEX_DICT['CONST']), term):
                append_to[-1].append(self.term_as_dict(term, 'Constante'))
            elif re.match("^({})$".format(REGEX_DICT['PARENTHESES_CLOSE']), term):
                if len(append_to) == 1:
                    return [self.term_as_dict(
                        term, 'Parenthese fermante supplimentaire', True
                    )]
                else:
                    append_to.pop()
            elif not re.match("^(({})|({}))$".format(REGEX_DICT['COMMA'], REGEX_DICT['SPACE']), term):
                return [self.term_as_dict(term, 'Terme pas definie')]

            separated_terms.pop(0)

        if len(append_to) > 1:
            return [self.term_as_dict('Erreur', "Un ')' est manquant", True)]
        return defined_terms


app = QApplication(sys.argv)
window = MainWindow()
window.resize(430, 500)
window.move(80, 100)
window.show()

app.exec_()
