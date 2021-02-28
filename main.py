#!/bin/python3

from os import error
from PyQt5.QtGui import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QMargins, left

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
            lexical_left = self.lexical_analysis(left_input.text())
            lexical_right = self.lexical_analysis(right_input.text())
            ops_left.append(self.terms_separator(lexical_left))
            ops_right.append(self.terms_separator(lexical_right))
            ops_left[-1] = self.syntax_analysis(ops_left[-1])[0]
            ops_right[-1] = self.syntax_analysis(ops_right[-1])[0]

            self.terms_table_holder.insertPlainText(
                '---------------------------------------------------\n'
                '1er terme: ----------\n' +
                (self.terms_table(ops_left[-1]) or '<Pas des termes>\n') +
                '2eme terme: ----------\n' +
                (self.terms_table(ops_right[-1]) or '<Pas des termes>\n')
            )

        self.unification_engine(ops_left, ops_right)

    def terms_table(self, defined_term):
        terms_str = "{}: {}\n".format(
            self.normlize_match(defined_term), defined_term['message']
        )

        if defined_term['message'] == 'Fonction':
            for fun_term in defined_term['terms']:
                terms_str += self.terms_table(fun_term)

        return terms_str

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
                return [self.term_as_dict(term, 'Terme pas definie', True)]

            separated_terms.pop(0)

        if len(append_to) > 1:
            return [self.term_as_dict('Erreur', "Un ')' est manquant", True)]
        return defined_terms

    def error_checker(self, terms_list: list):
        """
        called by unification engine, checks if there were any syntaxic errors
        before proceeding to the unification
        """
        if len(terms_list) == 0:
            return False
        elif terms_list[0]['error']:
            return True
        elif terms_list[0]['message'] == 'Fonction':
            return self.error_checker(terms_list[0]['terms']) or self.error_checker(terms_list[1:])
        return self.error_checker(terms_list[1:])

    def normlize_match(self, the_dict: dict):
        """
        return a match without the parentheses (in case of a function)
        """
        return the_dict['match'][:-2] if re.match(
            "^{}$".format(REGEX_DICT['FUNCTION'][:-1]),
            the_dict['match']
        ) else the_dict['match'][:-1] if re.match(
            "^{}$".format(REGEX_DICT['FUNCTION']),
            the_dict['match']
        ) else the_dict['match']

    def op_replacer(self, operations: list, old_op: dict, new_op: dict):
        """
        used on the 4th rule where every occurance of a term that matches old_op is replaced with new_op properties
        """
        if len(operations) == 0:
            return
        if operations[0]['match'] == old_op['match']:
            if not (operations[0]['message'] == old_op['message'] == 'Fonction'
                    ) or len(operations[0]['terms']) == len(old_op['terms']):
                operations[0]['message'] = new_op['message']
                operations[0]['match'] = new_op['match']
                if operations[0]['message'] == 'Fonction':
                    operations[0]['terms'] = new_op['terms']
        if operations[0]['message'] == 'Fonction':
            self.op_replacer(operations[0]['terms'], old_op, new_op)
        self.op_replacer(operations[1:], old_op, new_op)

    def occu_detector(self, operations: list, match: str):
        """
        detects if a term is in one of the operations sent
        """
        if len(operations) == 0:
            return False
        elif operations[0]['match'] == match:
            return True
        elif operations[0]['message'] == 'Fonction':
            return self.occu_detector(operations[0]['terms'], match) or self.occu_detector(operations[1:], match)
        return self.occu_detector(operations[1:], match)

    def term_str(self, term):
        if term['message'] == 'Fonction':
            return '{}({})'.format(self.normlize_match(term), ', '.join([
                self.term_str(aterm) for aterm in term['terms']
            ]))
        else:
            return term['match']

    def __rule_detector(self, ops_left, ops_right):
        the_dict = {
            'message': '',
            'error': False,
            'new_ops_left': [],
            'new_ops_right': []
        }

        for op_left, op_right, index in zip(ops_left, ops_right, range(1, len(ops_left) + 1)):
            if op_left['message'] == 'Constante':
                if op_right['message'] == 'Constante':
                    if op_left['match'] == op_right['match']:
                        the_dict['message'] += 'On applique la règle 2 sur ({})\n'.format(
                            index
                        )
                    else:
                        the_dict['new_ops_left'] += [
                            *ops_left[index:], op_left
                        ]
                        the_dict['new_ops_right'] += [
                            *ops_right[index:], op_right
                        ]

                        the_dict['message'] += '{} ≠ {}, Unification Impossible\n'.format(
                            op_left['match'],
                            op_right['match']
                        )
                        the_dict['error'] = True
                        break
                else:  # op_right is a variable or a function
                    the_dict['message'] += 'On applique la règle 1 sur ({})\n'.format(
                        index
                    )
                    the_dict['new_ops_left'].append(op_right)
                    the_dict['new_ops_right'].append(op_left)
            elif op_left['message'] == 'Variable':
                if op_right['message'] == 'Fonction':
                    if self.occu_detector(
                        op_right['terms'], op_left['match']
                    ):  # ex: x = f(x), x should not be on the right side
                        the_dict['new_ops_left'] += [
                            *ops_left[index:], op_left
                        ]
                        the_dict['new_ops_right'] += [
                            *ops_right[index:], op_right
                        ]

                        the_dict['message'] += '\'{}\' ne doit pas être en la partie droite \'{}\' de l\'équation, Unification Impossible\n'.format(
                            op_left['match'],
                            self.term_str(op_right)
                        )
                        the_dict['error'] = True
                        break

                if op_left['match'] == op_right['match']:
                    the_dict['message'] += 'On applique la règle 2 sur ({})\n'.format(
                        index
                    )
                    break
                elif 'treated' in op_left.keys():
                    the_dict['new_ops_left'].append(op_left)
                    the_dict['new_ops_right'].append(op_right)
                else:
                    pre_ops_l = the_dict[
                        'new_ops_left'] + ops_left[index:]
                    pre_ops_r = the_dict[
                        'new_ops_right'] + ops_right[index:]

                    if self.occu_detector(pre_ops_l + pre_ops_r, op_left['match']):
                        op_left['treated'] = True
                        self.op_replacer(
                            pre_ops_l + pre_ops_r, op_left, op_right
                        )

                        the_dict['new_ops_left'] = [*pre_ops_l, op_left]
                        the_dict['new_ops_right'] = [*pre_ops_r, op_right]

                        the_dict['message'] += 'On applique la règle 4 pour {}\n'.format(
                            index
                        )
                        break
                    else:
                        the_dict['new_ops_left'].append(op_left)
                        the_dict['new_ops_right'].append(op_right)

            else:  # op_left is a function
                if op_right['message'] == 'Fonction':
                    if op_left['match'] == op_right['match']:
                        if len(op_left['terms']) == len(op_right['terms']):
                            the_dict[
                                'new_ops_left'] += op_left['terms'] + ops_left[index:]
                            the_dict[
                                'new_ops_right'] += op_right['terms'] + ops_right[index:]

                            the_dict['message'] += 'On applique la règle 3 sur ({})\n'.format(
                                index
                            )
                            break
                        else:  # two functions with not the same number of arguments
                            the_dict['new_ops_left'] += [
                                *ops_left[index:], op_left
                            ]
                            the_dict['new_ops_right'] += [
                                *ops_right[index:], op_right
                            ]

                            the_dict['message'] += 'nombre des paramètres entre \'{}\' et \'{}\' ne sont pas égaux, Unification Impossible\n'.format(
                                self.term_str(op_left),
                                self.term_str(op_right)
                            )
                            the_dict['error'] = True
                            break
                    else:  # two functions with not the same name
                        the_dict['new_ops_left'] += [
                            *ops_left[index:], op_left
                        ]
                        the_dict['new_ops_right'] += [
                            *ops_right[index:], op_right
                        ]

                        the_dict['message'] += 'les fonctions \'{}\' et \'{}\' n\'ont pas le même nom, Unification Impossible\n'.format(
                            self.term_str(op_left),
                            self.term_str(op_right)
                        )
                        the_dict['error'] = True
                        break
                elif op_right['message'] == 'Variable':
                    the_dict['message'] += 'On applique la règle 1 sur ({})\n'.format(
                        index
                    )
                    the_dict['new_ops_left'].append(op_right)
                    the_dict['new_ops_right'].append(op_left)
                else:  # op_right is a constant
                    if 'treated' in op_left.keys():
                        the_dict['new_ops_left'].append(op_left)
                        the_dict['new_ops_right'].append(op_right)
                    else:
                        pre_ops_l = the_dict[
                            'new_ops_left'] + ops_left[index:]
                        pre_ops_r = the_dict[
                            'new_ops_right'] + ops_right[index:]

                        if self.occu_detector(pre_ops_l + pre_ops_r, op_left['match']):
                            op_left['treated'] = True
                            self.op_replacer(
                                pre_ops_l + pre_ops_r, op_left, op_right
                            )

                            the_dict['new_ops_left'] = [*pre_ops_l, op_left]
                            the_dict['new_ops_right'] = [*pre_ops_r, op_right]

                            the_dict['message'] += 'On applique la règle 4 pour {}\n'.format(
                                index
                            )
                            break
        return the_dict

    def unification_str(self, unification: dict, as_substitution=False):
        ops_left, ops_right = unification['new_ops_left'], unification['new_ops_right']
        unification_text = 'O={' if as_substitution else unification['message']

        if as_substitution:
            unification_text += ', '.join(map(lambda op_left, op_right: '{}/{}'.format(
                self.term_str(op_left), self.term_str(op_right)
            ), ops_left, ops_right)) + '}'
        else:
            for op_left, op_right, index in zip(ops_left, ops_right, range(1, len(ops_left) + 1)):
                unification_text += ('{}) {} = {}\n'.format(
                    index, self.term_str(op_left), self.term_str(op_right)
                ))

        if len(ops_left) == 0:
            unification_text += '<Pas des opérations>\n'

        return unification_text

    def unification_engine(self, ops_left: list, ops_right: list):
        # clears previous unification if any
        self.unification_holder.setPlainText('')

        # check numner of terms on left is equal to their number on the right
        try:
            assert len(ops_left) == len(ops_right)
        except AssertionError:
            self.unification_holder.appendPlainText(
                'Le nombre des termes à gauche ≠ Le nombre des termes à droite\n'
            )
            return

        # check any syntaxic errors generated before proceeding
        try:
            # for op_left, op_right in zip(ops_left, ops_right):
            assert not self.error_checker(ops_left)
            assert not self.error_checker(ops_right)
        except AssertionError:
            self.unification_holder.appendPlainText(
                'Il y\' un erreur dans l\'analyse syntaxique'
            )
            return

        prev_unification = {
            'message': '',
            'new_ops_left': ops_left,
            'new_ops_right': ops_right
        }
        unification = self.__rule_detector(ops_left, ops_right)

        self.unification_holder.appendPlainText(
            'On lance avec:\n' +
            self.unification_str(prev_unification)

        )

        while len(unification['message']):
            # loop stops when there is no new rule applied or error occured
            self.unification_holder.appendPlainText(
                self.unification_str(unification)
            )
            if unification['error']:
                break

            prev_unification = unification
            unification = self.__rule_detector(
                unification['new_ops_left'],
                unification['new_ops_right']
            )
        else:
            if len(prev_unification['message']) == 0:
                self.unification_holder.appendPlainText(
                    'Aucun changement à faire sur:\n' +
                    self.unification_str(prev_unification, True)
                )
            else:
                self.unification_holder.appendPlainText(
                    'L\'Unification a terminée avec succès\n' +
                    self.unification_str(prev_unification, True)
                )


app = QApplication(sys.argv)
window = MainWindow()
window.resize(750, 500)
window.move(80, 100)
window.show()

app.exec_()
