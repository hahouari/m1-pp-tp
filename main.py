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

# used in lexical_analysis
# regex = re.compile(
#     "|".join(REGEX_DICT.values())
# )

regex = r"\"[^\"]*\"|[-+]?[\w_\.]+(\(\)?)?|\)|,|[ ]+"

# a FIFO that holds a function until finding its closing parentheses ')'
interpretation_queue = []


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Master 1 - Paradigmes de Programmation")

        g_layout = QVBoxLayout(self)
        terms_layout = QHBoxLayout(self)

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
        terms_text = self.lexical_analysis(self.terms_input.text())
        terms_list = self.terms_separator(terms_text)
        print(terms_list)
        terms_list = self.syntax_analysis(terms_list)
        self.terms_table_holder.setPlainText(self.terms_table(terms_list))

    def terms_table(self, defined_terms):
        terms_str = ""
        for term in defined_terms:
            terms_str += "{}: {}\n".format(term['match'][:-2] if re.match(
                "^{}$".format(REGEX_DICT['FUNCTION'][:-1]),
                term['match']
            ) else term['match'][:-1] if re.match(
                "^{}$".format(REGEX_DICT['FUNCTION']),
                term['match']
            ) else term['match'], term['message'])
        return terms_str

    def lexical_analysis(self, input_text):
        return re.sub(regex, lambda amatch: "{}#".format(amatch.group()), input_text)

    def terms_separator(self, terms_text: str):
        terms_list = terms_text.split("#")
        if len(terms_list) and terms_list[-1] == "":
            terms_list.pop()
        return terms_list

    def term_as_dict(self, match, message):
        return {
            "match": match,
            "message": message
        }

    def syntax_analysis(self, separated_terms: list):
        defined_terms = []
        while len(separated_terms):
            term = separated_terms[0]
            # functions need a queue to know if its closed parenthese
            if re.match("^({})$".format(REGEX_DICT['FUNCTION']), term):
                if re.match("^({})$".format(REGEX_DICT['FUNCTION'][:-1]), term):
                    interpretation_queue.clear()
                    defined_terms = [self.term_as_dict(
                        term, 'Erreur, Fonction sans des paramètres'
                    )]
                    break
                function_term = self.term_as_dict(term, 'Fonction')
                interpretation_queue.append(function_term)
                defined_terms.append(function_term)
            elif re.match("^({})$".format(REGEX_DICT['PARENTHESES_OPEN']), term):
                open_parentheses_term = self.term_as_dict(term, '')
                interpretation_queue.append(open_parentheses_term)
            elif re.match("^({})$".format(REGEX_DICT['VARIABLE']), term):
                defined_terms.append(self.term_as_dict(term, 'Variable'))
            elif re.match("^({})$".format(REGEX_DICT['CONST']), term):
                defined_terms.append(self.term_as_dict(term, 'Constante'))
            elif re.match("^({})$".format(REGEX_DICT['PARENTHESES_CLOSE']), term):
                if len(interpretation_queue) > 0:
                    interpretation_queue.pop()
                else:
                    defined_terms = [self.term_as_dict(
                        term, 'Parenthese fermante supplimentaire')]
                    break
            elif not re.match("^(({})|({}))$".format(REGEX_DICT['COMMA'], REGEX_DICT['SPACE']), term):
                defined_terms = [self.term_as_dict(term, 'Terme pas definie')]
                break
            separated_terms.pop(0)

        if len(interpretation_queue) > 0:
            uncompleted_functions = []
            while len(interpretation_queue) > 0:
                unexpected_term = interpretation_queue[0]
                del interpretation_queue[0]
                uncompleted_functions.append(self.term_as_dict(
                    unexpected_term['match'],
                    "Parenthese ouvrante pas fermee avec ')'" if unexpected_term['match'] == "(" else "Fonction pas fermee avec ')'"))
            return uncompleted_functions
        return defined_terms


app = QApplication(sys.argv)
window = MainWindow()
window.resize(500, 380)
window.move(80, 100)
window.show()

app.exec_()
