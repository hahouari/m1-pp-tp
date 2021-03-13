from regle import Regle
from typing import List, Union
from terme import Terme
from equation import Equation


class Unification:
    def __init__(self, equations: List[Equation]) -> None:
        self.feedback = 'On lance avec:\n'
        self.equations = equations
        self.erreur = False

    def __str__(self):
        if len(self.equations) == 0 and self.feedback:
            return '\n{}<Pas des équations>\n'.format(self.feedback)

        est_substitution = len(self.feedback) == 0
        str_termes = '\nL\'Unification a terminée avec succès:\n  O={' if est_substitution else '\n{}'.format(
            self.feedback
        )

        if est_substitution:
            str_termes += ', '.join(map(lambda equation: '{}/{}'.format(
                equation.gauche, equation.droite
            ), self.equations)) + '}\n'
        else:
            for equation, index in zip(self.equations, range(0, len(self.equations))):
                str_termes += ('{}) {}\n'.format(
                    index+1, equation
                ))

        return str_termes

    def __params_verifier_erreur(self, sous_termes: List[Terme]):
        if len(sous_termes) == 0:
            return False

        for terme in sous_termes:
            if terme.erreur:
                return True
            if terme.type == 'Fonction':
                if self.__params_verifier_erreur(
                    terme.sous_termes
                ):
                    return True
        return self.__params_verifier_erreur(sous_termes[1:])

    def verifier_erreur(self, equations: List[Equation]) -> bool:
        """
        applée par moteur de l'unification, vérifie que il n'y a pas des erreurs avant aller a l'unification
        """
        if len(equations) == 0:
            return False

        equation = equations[0]
        if equation.gauche.erreur or equation.droite.erreur:
            return True
        if equation.gauche.type == 'Fonction':
            if self.__params_verifier_erreur(equation.gauche.sous_termes):
                return True
        if equation.droite.type == 'Fonction':
            if self.__params_verifier_erreur(equation.droite.sous_termes):
                return True
        return self.verifier_erreur(equations[1:])

    def moteur_unification(self):
        # check any syntaxic errors generated before proceeding
        try:
            assert not self.verifier_erreur(self.equations)
        except AssertionError:
            return 'Il y\'a une erreur dans l\'analyse syntaxique'

        unif_process_msg = str(self)

        while len(self.feedback) and not self.erreur:
            self.__unif_iter()
            unif_process_msg += str(self)

        return unif_process_msg[1:]

    def __unif_iter(self):
        self.feedback = ''
        old_equations = self.equations
        self.equations = []

        for equation, index in zip(old_equations, range(1, len(old_equations) + 1)):
            # this is for equation that generated impossible unification
            if equation.erreur:
                continue
            gauche, droite = equation.gauche, equation.droite
            if gauche.type == 'Constante':
                if droite.type == 'Constante':
                    if Regle.regle2(equation):
                        self.feedback += 'On applique la règle 2 sur ({})\n'.format(
                            index
                        )
                    else:
                        self.equations.extend([
                            equation, *old_equations[index:]
                        ])
                        self.feedback += '{} ≠ {}, Unification Impossible\n'.format(
                            gauche,
                            droite
                        )
                        equation.erreur = True
                        self.erreur = True
                        break
                else:  # op_right is a variable or a function
                    self.feedback += 'On applique la règle 1 sur ({})\n'.format(
                        index
                    )
                    self.equations.append(
                        Regle.regle1(gauche, droite)
                    )
            elif gauche.type == 'Variable':
                if droite.type == 'Fonction':
                    # ex: x = f(x), x should not be on the right side
                    if gauche.verifier_occurence(droite.sous_termes):
                        self.equations.extend([
                            equation, *old_equations[index:]
                        ])

                        self.feedback += '\'{}\' ne doit pas être en la partie droite \'{}\' de l\'équation, Unification Impossible\n'.format(
                            gauche,
                            droite
                        )
                        equation.erreur = True
                        self.erreur = True
                        break

                if gauche == droite:
                    self.feedback += 'On applique la règle 2 sur ({})\n'.format(
                        index
                    )
                    break
                else:
                    if Regle.regle4(self.equations + old_equations[index:], equation):
                        self.equations.extend([
                            equation, *old_equations[index:]
                        ])
                        self.feedback += 'On applique la règle 4 pour {}\n'.format(
                            index
                        )
                        break
                    else:
                        self.equations.append(equation)

            else:  # op_left is a function
                if droite.type == 'Fonction':
                    if gauche.match == droite.match:
                        if len(gauche.sous_termes) == len(droite.sous_termes):
                            self.equations.extend([
                                *Regle.regle3(
                                    equation.gauche.sous_termes,
                                    equation.droite.sous_termes
                                ),
                                *old_equations[index:]
                            ])

                            self.feedback += 'On applique la règle 3 sur ({})\n'.format(
                                index
                            )
                            break
                        else:  # two functions with not the same number of arguments
                            self.equations.extend([
                                equation,
                                *old_equations[index:]
                            ])

                            self.feedback += 'nombre des paramètres entre \'{}\' et \'{}\' ne sont pas égaux, Unification Impossible\n'.format(
                                gauche,
                                droite
                            )

                            equation.erreur = True
                            self.erreur = True
                            break
                    else:  # two functions that are not the same
                        self.equations.extend([
                            equation, *old_equations[index:]
                        ])

                        self.feedback += 'les fonctions \'{}\' et \'{}\' n\'ont pas le même nom, Unification Impossible\n'.format(
                            gauche,
                            droite
                        )

                        self.erreur = True
                        equation.erreur = True
                        break
                elif droite.type == 'Variable':
                    self.feedback += 'On applique la règle 1 sur ({})\n'.format(
                        index
                    )
                    self.equations.append(Regle.regle1(gauche, droite))
                else:  # op_right is a constant
                    if Regle.regle4(self.equations + old_equations[index:], equation):
                        self.equations.extend([
                            equation, *old_equations[index:]
                        ])
                        self.feedback += 'On applique la règle 4 pour {}\n'.format(
                            index
                        )
                        break
                    else:
                        self.equations.append(equation)
