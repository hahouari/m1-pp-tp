from PyQt5.QtGui import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QMargins

from queue import Queue
import sys
import re

# regex dict definition, used by regex to produce global regex, and syntax_analysis
REGEX_DICT = {}
REGEX_DICT['PARENTHESES_CLOSE'] = r"[ ]*\)[ ]*"
REGEX_DICT['CONST'] = r"[ ]*\-?(\.\d+|\d+(\.\d*)?)[ ]*"
REGEX_DICT['FUNCTION'] = r"[ ]*[a-zA-Z][\w\s]*\([ ]*"
REGEX_DICT['VARIABLE'] = r"[ ]*[a-zA-Z][\w\s]*[ ]*"
REGEX_DICT['COMMA'] = r"[ ]*,[ ]*"
REGEX_DICT['STRING'] = r"[ ]*'[^\']*'|\"[^\"]*\"[ ]*"
REGEX_DICT['PARENTHESES_OPEN'] = r"[ ]*\([ ]*"

# used in lexical_analysis
regex = re.compile(
    "|".join(REGEX_DICT.values())
)

# a FIFO that holds a function arguments, holds the function arguments until finding the closing parentheses ')'
# so that all
interpretation_queue = Queue()

class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Master 1 - Paradigms de Programmation")

        g_layout = QVBoxLayout(self)
        terms_layout = QHBoxLayout(self)

        term_label = QLabel("Inserer les termes:", self)

        self.terms_input = QLineEdit(self)
        self.terms_input.textEdited.connect(self.on_validate)

        self.term_types_table = QPlainTextEdit()
        self.term_types_table.setReadOnly(True)

        validate_button = QPushButton(QIcon('animal-penguin.png'), "Valider", self)
        validate_button.clicked.connect(self.on_validate)

        terms_layout.addWidget(self.terms_input)
        terms_layout.addWidget(validate_button)
        terms_layout.setContentsMargins(QMargins())

        terms_widget = QWidget()
        terms_widget.setLayout(terms_layout)
        

        g_layout.addWidget(term_label)
        g_layout.addWidget(terms_widget)
        ##################### LIVE REGEX FOR LIVE TESTING
        # self.regex_input = QLineEdit()
        # self.regex_input.setPlaceholderText('override regex')
        # self.regex_input.textEdited.connect(self.regex_update)
        # g_layout.addWidget(self.regex_input)
        #####################
        g_layout.addWidget(self.term_types_table)

        widget = QWidget()
        widget.setLayout(g_layout)

        self.setCentralWidget(widget)

    def on_validate(self):
        terms_text = self.lexical_analysis(self.terms_input.text())
        terms_list = self.terms_separator(terms_text)
        print(terms_list)
        print(self.syntax_analysis(terms_list))
        self.term_types_table.setPlainText(terms_text)

    def lexical_analysis(self, input_text):
        return re.sub(regex, lambda amatch: "{}#".format(amatch.group()), input_text)

    def terms_separator(self, terms_text: str):
        terms_list = terms_text.split("#")
        if len(terms_list) and terms_list[-1] == "":
            terms_list.pop()
        return terms_list

    def term_as_dict(self, term, type):
        return {
            "term": term,
            "type": type
        }

    def syntax_analysis(self, separated_terms: list):
        defined_terms = []
        while len(separated_terms):
            term = separated_terms[0]
            if re.match("^{}$".format(REGEX_DICT['FUNCTION']), term) or re.match("^{}$".format(REGEX_DICT['PARENTHESES_OPEN']), term):
                interpretation_queue.put(self.term_as_dict(")", 'PARENTHESES_CLOSE'))
                defined_terms.append(self.term_as_dict(term, 'FUNCTION'))
            elif re.match("^{}$".format(REGEX_DICT['VARIABLE']), term):
                defined_terms.append(self.term_as_dict(term, 'VARIABLE'))
            elif re.match("^{}$".format(REGEX_DICT['STRING']), term):
                defined_terms.append(self.term_as_dict(term, 'STRING'))
            elif re.match("^{}$".format(REGEX_DICT['CONST']), term):
                defined_terms.append(self.term_as_dict(term, 'CONST'))
            elif re.match("^{}$".format(REGEX_DICT['PARENTHESES_CLOSE']), term):
                if interpretation_queue.qsize() > 0:
                    interpretation_queue.get()
                else:
                    defined_terms.append(self.term_as_dict(term, 'UNEXPECTED_CLOSING_PARENTHESES'))
            elif not re.match("^{}$".format(REGEX_DICT['COMMA']), term):
                defined_terms.append(self.term_as_dict(term, 'ENEXPECTED TERM'))

            separated_terms.pop(0)
        return defined_terms                    

    def regex_update(self):
        try:
            print(self.regex_input.text())
            global regex
            regex = re.compile(self.regex_input.text())
        except Exception as _:
            self.term_types_table.setPlainText("regex error")
            return
        self.on_validate()


app = QApplication(sys.argv)
window = MainWindow()
window.resize(500, 380)
window.move(80, 100)
window.show()

app.exec_()