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


def terms_table(defined_term):
    terms_str = "{}: {}\n".format(
        normlize_match(defined_term), defined_term['message']
    )

    if defined_term['message'] == 'Fonction':
        for fun_term in defined_term['terms']:
            terms_str += terms_table(fun_term)

    return terms_str


def lexical_analysis(input_text):
    return re.sub(regex, lambda amatch: "{}#".format(amatch.group()), input_text)


def terms_separator(terms_text: str):
    terms_list = terms_text.split("#")
    if len(terms_list) and terms_list[-1] == "":
        terms_list.pop()
    return terms_list


def term_as_dict(match, message, error=False):
    the_dict = {
        "match": match,
        "message": message,
        "error": error
    }

    if message == 'Fonction':
        the_dict['terms'] = []

    return the_dict


def syntax_analysis(separated_terms: list):
    defined_terms = []
    append_to = [defined_terms]
    while len(separated_terms):
        term = separated_terms[0]
        # functions need a queue to know if its closed parenthese
        if re.match("^({})$".format(REGEX_DICT['FUNCTION']), term):
            if term[-1] == ')':
                return [term_as_dict(
                    term, 'Erreur, Fonction sans des paramètres', True
                )]
            function_term = term_as_dict(term, 'Fonction')
            append_to[-1].append(function_term)
            append_to.append(function_term['terms'])
        # elif re.match("^({})$".format(REGEX_DICT['PARENTHESES_OPEN']), term):
            # open_parentheses_term = term_as_dict(term, '')
            # append_to.append(open_parentheses_term)
        elif re.match("^({})$".format(REGEX_DICT['VARIABLE']), term):
            append_to[-1].append(term_as_dict(term, 'Variable'))
        elif re.match("^({})$".format(REGEX_DICT['CONST']), term):
            append_to[-1].append(term_as_dict(term, 'Constante'))
        elif re.match("^({})$".format(REGEX_DICT['PARENTHESES_CLOSE']), term):
            if len(append_to) == 1:
                return [term_as_dict(
                    term, 'Parenthese fermante supplimentaire', True
                )]
            else:
                append_to.pop()
        elif not re.match("^(({})|({}))$".format(REGEX_DICT['COMMA'], REGEX_DICT['SPACE']), term):
            return [term_as_dict(term, 'Terme pas definie', True)]

        separated_terms.pop(0)

    if len(append_to) > 1:
        return [term_as_dict('Erreur', "Un ')' est manquant", True)]
    return defined_terms


def error_checker(terms_list: list):
    """
    called by unification engine, checks if there were any syntaxic errors
    before proceeding to the unification
    """
    if len(terms_list) == 0:
        return False
    elif terms_list[0]['error']:
        return True
    elif terms_list[0]['message'] == 'Fonction':
        return error_checker(terms_list[0]['terms']) or error_checker(terms_list[1:])
    return error_checker(terms_list[1:])


def normlize_match(the_dict: dict):
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


def op_replacer(operations: list, old_op: dict, new_op: dict):
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
        op_replacer(operations[0]['terms'], old_op, new_op)
    op_replacer(operations[1:], old_op, new_op)


def occu_detector(operations: list, match: str):
    """
    detects if a term is in one of the operations sent
    """
    if len(operations) == 0:
        return False
    elif operations[0]['match'] == match:
        return True
    elif operations[0]['message'] == 'Fonction':
        return occu_detector(operations[0]['terms'], match) or occu_detector(operations[1:], match)
    return occu_detector(operations[1:], match)


def term_str(term):
    if term['message'] == 'Fonction':
        return '{}({})'.format(normlize_match(term), ', '.join([
            term_str(aterm) for aterm in term['terms']
        ]))
    else:
        return term['match']


def __rule_detector(ops_left, ops_right):
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
                if occu_detector(
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
                        term_str(op_right)
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

                if occu_detector(pre_ops_l + pre_ops_r, op_left['match']):
                    op_left['treated'] = True
                    op_replacer(
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
                            term_str(op_left),
                            term_str(op_right)
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
                        term_str(op_left),
                        term_str(op_right)
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

                    if occu_detector(pre_ops_l + pre_ops_r, op_left['match']):
                        op_left['treated'] = True
                        op_replacer(
                            pre_ops_l + pre_ops_r, op_left, op_right
                        )

                        the_dict['new_ops_left'] = [*pre_ops_l, op_left]
                        the_dict['new_ops_right'] = [*pre_ops_r, op_right]

                        the_dict['message'] += 'On applique la règle 4 pour {}\n'.format(
                            index
                        )
                        break
    return the_dict


def unification_str(unification: dict, as_substitution=False):
    ops_left, ops_right = unification['new_ops_left'], unification['new_ops_right']
    unification_text = 'O={' if as_substitution else unification['message']

    if as_substitution:
        unification_text += ', '.join(map(lambda op_left, op_right: '{}/{}'.format(
            term_str(op_left), term_str(op_right)
        ), ops_left, ops_right)) + '}'
    else:
        for op_left, op_right, index in zip(ops_left, ops_right, range(1, len(ops_left) + 1)):
            unification_text += ('{}) {} = {}\n'.format(
                index, term_str(op_left), term_str(op_right)
            ))

    if len(ops_left) == 0:
        unification_text += '<Pas des opérations>\n'

    return unification_text


def unification_engine(ops_left: list, ops_right: list):

    # check numner of terms on left is equal to their number on the right
    try:
        assert len(ops_left) == len(ops_right)
    except AssertionError:
        return 'Le nombre des termes à gauche ≠ Le nombre des termes à droite\n'

    # check any syntaxic errors generated before proceeding
    try:
        # for op_left, op_right in zip(ops_left, ops_right):
        assert not error_checker(ops_left)
        assert not error_checker(ops_right)
    except AssertionError:
        return 'Il y\' un erreur dans l\'analyse syntaxique'

    prev_unification = {
        'message': '',
        'new_ops_left': ops_left,
        'new_ops_right': ops_right
    }
    unification = __rule_detector(ops_left, ops_right)

    unification_text = (
        'On lance avec:\n' +
        unification_str(prev_unification)
    )

    while len(unification['message']):
        # loop stops when there is no new rule applied or error occured
        unification_text += (
            unification_str(unification)
        )
        if unification['error']:
            break

        prev_unification = unification
        unification = __rule_detector(
            unification['new_ops_left'],
            unification['new_ops_right']
        )
    else:
        if len(prev_unification['message']) == 0:
            unification_text += (
                'Aucun changement à faire sur:\n' +
                unification_str(prev_unification, True)
            )
        else:
            unification_text += (
                'L\'Unification a terminée avec succès\n' +
                unification_str(prev_unification, True)
            )

    return unification_text
