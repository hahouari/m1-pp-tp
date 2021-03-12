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


# a FIFO that holds a function until finding its closing parentheses ')'
interpretation_queue = []


def terms_table(defined_terms):
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


def lexical_analysis(input_text):
    return re.sub(regex, lambda amatch: "{}#".format(amatch.group()), input_text)


def terms_separator(terms_text: str):
    terms_list = terms_text.split("#")
    if len(terms_list) and terms_list[-1] == "":
        terms_list.pop()
    return terms_list


def term_as_dict(match, message):
    return {
        "match": match,
        "message": message
    }


def syntax_analysis(separated_terms: list):
    defined_terms = []
    while len(separated_terms):
        term = separated_terms[0]
        # functions need a queue to know if its closed parenthese
        if re.match("^({})$".format(REGEX_DICT['FUNCTION']), term):
            if re.match("^({})$".format(REGEX_DICT['FUNCTION'][:-1]), term):
                interpretation_queue.clear()
                defined_terms = [term_as_dict(
                    term, 'Erreur, Fonction sans des paramètres'
                )]
                break
            function_term = term_as_dict(term, 'Fonction')
            interpretation_queue.append(function_term)
            defined_terms.append(function_term)
        elif re.match("^({})$".format(REGEX_DICT['PARENTHESES_OPEN']), term):
            open_parentheses_term = term_as_dict(term, '')
            interpretation_queue.append(open_parentheses_term)
        elif re.match("^({})$".format(REGEX_DICT['VARIABLE']), term):
            defined_terms.append(term_as_dict(term, 'Variable'))
        elif re.match("^({})$".format(REGEX_DICT['CONST']), term):
            defined_terms.append(term_as_dict(term, 'Constante'))
        elif re.match("^({})$".format(REGEX_DICT['PARENTHESES_CLOSE']), term):
            if len(interpretation_queue) > 0:
                interpretation_queue.pop()
            else:
                defined_terms = [term_as_dict(
                    term, 'Parenthese fermante supplimentaire')]
                break
        elif not re.match("^(({})|({}))$".format(REGEX_DICT['COMMA'], REGEX_DICT['SPACE']), term):
            defined_terms = [term_as_dict(term, 'Terme pas definie')]
            break
        separated_terms.pop(0)

    if len(interpretation_queue) > 0:
        uncompleted_functions = []
        while len(interpretation_queue) > 0:
            unexpected_term = interpretation_queue[0]
            del interpretation_queue[0]
            uncompleted_functions.append(term_as_dict(
                unexpected_term['match'],
                "Parenthese ouvrante pas fermee avec ')'" if unexpected_term['match'] == "(" else "Fonction pas fermee avec ')'"))
        return uncompleted_functions
    return defined_terms
