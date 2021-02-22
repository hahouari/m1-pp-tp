% taille d'une arbre
% taille_arb([[]], _):-!, write('[] is supplied instead of an X value.'), fail.
% taille_arb([[], _], _):-!, write('[] is supplied instead of an X value.'), fail.
% taille_arb([[], _, _], _):-!, write('[] is supplied instead of an X value.'), fail.
taille_arb([X, [], Z], L):-!, taille_arb([X, Z], L). % just put the Z in place of Y
taille_arb([_, Y, Z], L):-!, taille_arb(Y, L1), taille_arb(Z, L2), L is 1 + L1 + L2.
taille_arb([_, Y], L):-!, taille_arb(Y, L1), L is 1 + L1.
taille_arb([_], L):-!, L is 1.
taille_arb([], L):- !, L is 0.
taille_arb(_, L):- !, L is 1.
taille_arb(_):- writef('Call as taille_arb(<Arbre>, L) argument.'), fail.

% nombre des feuilles d'une arbre
% leaves_list([[]], _):-!, write('[] is supplied instead of an X value.'), fail.
% leaves_list([[], _], _):-!, write('[] is supplied instead of an X value.'), fail.
% leaves_list([[], _, _], _):-!, write('[] is supplied instead of an X value.'), fail.
leaves_list([X, [], []], F):-!, F is X.
leaves_list([X, [], Z], F):-!, leaves_list([X, Z], F).
leaves_list([_, Y, Z], [F1, F2]):-!, leaves_list(Y, F1), leaves_list(Z, F2).
leaves_list([X, []], F):-!, F is X.
leaves_list([_, Y], F1):-!, leaves_list(Y, F1).
leaves_list([X], F):-!, F is X.
leaves_list(X, F):-!, F is X.
leaves_list(_):- writef('Call as leaves_list(<Arbre>, F) argument.'), fail.

% niveau d'un noeud dans une arbre
% node_niv([[]], _):-!, write('[] is supplied instead of an X value.'), fail.
% node_niv([[], _], _):-!, write('[] is supplied instead of an X value.'), fail.
% node_niv([[], _, _], _):-!, write('[] is supplied instead of an X value.'), fail.
node_niv([X], X, N):- !, N is 0.
node_niv([X, _], X, N):- !, N is 0.
node_niv([X, _, _], X, N):- !, N is 0.
node_niv([_X1], _X2, N):- !, N is -1.
node_niv([_, Y], X2, N):- !, node_niv(Y, X2, N1), eval_n(N1, N).
node_niv([X1, [], Z], X2, N):-!, node_niv([X1, Z], X2, N).
node_niv([X1, Y, []], X2, N):-!, node_niv([X1, Y], X2, N).
node_niv([_, Y, Z], X2, N):- !, node_niv(Y, X2, N1), node_niv(Z, X2, N2), N3 is max(N1, N2), eval_n(N3, N).
node_niv(A, X, N):- !, node_niv(A, X, N).
node_niv(A, _):- !, node_niv(A).
node_niv(_):- writef('Call as node_niv(<Arbre>, <an X>, N) argument.'), fail.
% used by node_niv, N2 will take -1 if N1 = -1, otherwise it takes N1 + 1, looks like the NOT predicate
eval_n(N1, N2):- N1 = -1, !, N2 is N1.
eval_n(N1, N2):- !, N2 is N1 + 1.


