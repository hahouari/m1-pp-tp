import re
from terme import Terme


class Analyse:
    def analyse_lexical(text: str):
        """
        recevoir un texte et le séparer par l'ajout du symbole # après chaque terme.
        """
        return re.sub(Terme.RE_TOUS, lambda amatch: "{}#".format(amatch.group()), text)

    def analyse_syntaxique(liste_termes: list):
        termes_definies = []
        append_to = [termes_definies]
        while len(liste_termes):
            terme = liste_termes[0]
            # functions need a queue to know if its closed parenthese
            if re.match("^({})$".format(Terme.RE_FONCTION), terme):
                if terme[-1] == ')':
                    return [
                        Terme(
                            terme,
                            'Erreur, Fonction sans des paramètres',
                            True
                        )
                    ]
                function_term = Terme(
                    terme,
                    'Fonction'
                )
                append_to[-1].append(function_term)
                append_to.append(function_term.sous_termes)
            # elif re.match("^({})$".format(Terme.RE_PARENTHESE_OUVRANTE), terme):
                # open_parentheses_term = self.term_as_dict(terme, '')
                # append_to.append(open_parentheses_term)
            elif re.match("^({})$".format(Terme.RE_VARIABLE), terme):
                append_to[-1].append(Terme(
                    terme,
                    'Variable'
                ))
            elif re.match("^({})$".format(Terme.RE_CONST), terme):
                append_to[-1].append(Terme(
                    terme,
                    'Constante'
                ))
            elif re.match("^({})$".format(Terme.RE_PARENTHESE_FERMANTE), terme):
                if len(append_to) == 1:
                    return [Terme(
                        'Erreur',
                        'Parenthese fermante supplimentaire',
                        True
                    )]
                else:
                    append_to.pop()
            elif not re.match("^(({})|({}))$".format(Terme.RE_COMMA, Terme.RE_ESPACE), terme):
                return [Terme(
                    terme,
                    'Terme pas definie',
                    True
                )]

            liste_termes.pop(0)

        if len(append_to) > 1:
            return [Terme(
                'Erreur',
                "Un ')' est manquant",
                True
            )]
        return termes_definies

    def termes_separateur(text: str):
        """
        transfèrer les termes analysés par l'analyseur lexical à une liste des termes.
        """
        liste_termes = text.split("#")
        if len(liste_termes) and liste_termes[-1] == "":
            liste_termes.pop()
        return liste_termes
