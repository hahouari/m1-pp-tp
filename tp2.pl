% taille d'une arbre
taille_arb([[X], _, _], _):-!, writef('[%w] is supplied instead of %w.', [X, X]), fail.
taille_arb([[], _, _], _):-!, write('[] is supplied instead of an X value.'), fail.
taille_arb([_,Y,Z], L):-!, taille_arb(Y, L1), taille_arb(Z, L2), L is 1 + L1 + L2.
taille_arb([_,Y], L):-!, taille_arb(Y, L1), L is 1 + L1.
taille_arb([_], L):-!, L is 1.
taille_arb([], L):- !, L is 0.
taille_arb(_, L):- !, L is 1.
taille_arb(L):- !, L is 0.


