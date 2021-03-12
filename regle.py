from terme import Terme
from equation import Equation
from typing import List


class Regle:
    def regle1(gauche: Terme, droite: Terme):
        return Equation(droite, gauche)

    def regle2(equation: Equation):
        return equation.gauche == equation.droite

    def regle3(g_sous_termes: List[Terme], d_sous_termes: List[Terme]) -> List[Equation]:
        return [Equation(g_terme, d_terme) for g_terme, d_terme in zip(
            g_sous_termes,
            d_sous_termes
        )]

    def regle4(equations: List[Equation], sele_eq: Equation):
        if Regle.verifier_occurence(equations, sele_eq.gauche):
            Regle.__terme_remplaceur(equations, sele_eq.gauche, sele_eq.droite)
            return True
        return False

    def verifier_occurence(equations: List[Equation], terme: Terme):
        """
        detects if a term is in one of the equations sent
        """
        if len(equations) == 0:
            return False

        equation = equations[0]
        if equation.gauche == terme or equation.droite == terme:
            return True

        if equation.gauche.type == 'Fonction':
            if terme.verifier_occurence(equation.gauche.sous_termes):
                return True
        if equation.droite.type == 'Fonction':
            if terme.verifier_occurence(equation.droite.sous_termes):
                return True
        return Regle.verifier_occurence(equations[1:], terme)

    def __params_remplaceur(sous_termes: List[Terme], old_terme: Terme, new_terme: Terme):
        new_sous_termes: List[Terme] = []
        for terme in sous_termes:
            new_sous_termes.append(
                new_terme if terme == old_terme else terme
            )
            if terme.type == 'Fonction':
                terme.sous_termes = Regle.__params_remplaceur(
                    terme.sous_termes, old_terme, new_terme
                )
        return new_sous_termes

    def __terme_remplaceur(equations: List[Equation], old_terme: Terme, new_terme: Terme):
        """
        used on the 4th rule where every occurance of the old term is replaced with new term
        """
        if len(equations) == 0:
            return

        equation = equations[0]
        if equation.gauche == old_terme:
            equation.gauche = new_terme
        elif equation.gauche.type == 'Fonction':
            equation.gauche.sous_termes = Regle.__params_remplaceur(
                equation.gauche.sous_termes, old_terme, new_terme
            )
        if equation.droite == old_terme:
            equation.droite = new_terme
        elif equation.droite.type == 'Fonction':
            equation.droite.sous_termes = Regle.__params_remplaceur(
                equation.droite.sous_termes, old_terme, new_terme
            )

        Regle.__terme_remplaceur(equations[1:], old_terme, new_terme)
