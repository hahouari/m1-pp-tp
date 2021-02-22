% taille d'une arbre
taille_arb([_, Y, Z], L):-!, taille_arb(Y, L1), taille_arb(Z, L2), L is 1 + L1 + L2.
taille_arb([_, Y], L):-!, taille_arb(Y, L1), L is 1 + L1.
taille_arb([_], L):-!, L is 1.
taille_arb([], L):- !, L is 0.
taille_arb(_, L):- !, L is 1.
taille_arb(_):- writef('Call as taille_arb(<Arbre>, L) argument.'), fail.

% nombre des feuilles d'une arbre
leaves_list([X, [], []], F):-!, F is X.
leaves_list([X, [], Z], F):-!, leaves_list([X, Z], F).
leaves_list([_, Y, Z], F3):-!, leaves_list(Y, F1), leaves_list(Z, F2), flatten2([F1, F2], F3).
leaves_list([X, []], F):-!, F is X.
leaves_list([_, Y], F1):-!, leaves_list(Y, F1).
leaves_list([X], F):-!, F is X.
leaves_list(X, F):-!, F is X.
leaves_list(_):- writef('Call as leaves_list(<Arbre>, F) argument.'), fail.

% found on https://stackoverflow.com/questions/9059572/flatten-a-list-in-prolog
% used because the Leaves are returned as a nested list.
flatten2([], []):- !.
flatten2([L|Ls], FlatL) :- !, flatten2(L, NewL), flatten2(Ls, NewLs), append(NewL, NewLs, FlatL).
flatten2(L, [L]).

% niveau d'un noeud dans une arbre
node_niv([X], X, N):- !, N is 0.
node_niv([X, _], X, N):- !, N is 0.
node_niv([X, _, _], X, N):- !, N is 0.
node_niv([_X1], _X2, N):- !, N is -1.
node_niv([_, Y], X2, N):- !, node_niv(Y, X2, N1), eval_n(N1, N).
node_niv([X1, [], Z], X2, N):-!, node_niv([X1, Z], X2, N).
node_niv([X1, Y, []], X2, N):-!, node_niv([X1, Y], X2, N).
node_niv([_, Y, Z], X2, N):- !, node_niv(Y, X2, N1), node_niv(Z, X2, N2), N3 is max(N1, N2), eval_n(N3, N).
node_niv(A, _):- !, node_niv(A).
node_niv(_):- writef('Call as node_niv(<Arbre>, <an X>, N) argument.'), fail.

% used by node_niv, N2 will take -1 if N1 = -1, otherwise it takes N1 + 1, looks like the NOT predicate
eval_n(N1, N2):- N1 = -1, !, N2 is N1.
eval_n(N1, N2):- !, N2 is N1 + 1.

% inserer element dans un tas.
tas_insert(A, X, R):- !, boocle_niv(A, X, R, 0). % it all started here
tas_insert([X1], X2, [B, [S]], 0):- !, B is max(X1, X2), S is min(X1, X2).
tas_insert([_, _, _], _, _, 0):- !, fail. % if both children are full when reaching 0, R is the A itself
tas_insert([X1, Y, Z], X2, [X3, Y2, Z], N):- N1 is N-1, tas_insert(Y, X2, Y1, N1), !, sort_tas(Y1, X1, Y2, X3).
tas_insert([X1, Y, Z], X2, [X3, Y, Z2], N):- N1 is N-1, tas_insert(Z, X2, Z1, N1), !, sort_tas(Z1, X1, Z2, X3).
tas_insert([X1, Y], X2, [B, Y, [S]], 0):- !, B is max(X1, X2), S is min(X1, X2).
tas_insert(_):- writef('Call as tas_insert(<Arbre>, <an X>, R) argument.'), fail.

% le parcours en largeur avec l'appelle à tas_insert pour chaque niveau jusqu'a le X est inséré
boocle_niv(A, X, R, N1):- tas_insert(A, X, R, N1), !. % if inserted loop stops
boocle_niv(A, X, R, N1):- !, N2 is N1 + 1, boocle_niv(A, X, R, N2). % else it loops again with N+1

% changer enter la tete et X si le dernier est superieur à la tete, sinon tous rester le même
sort_tas([X1], X2, [S], B):- !, B is max(X1, X2), S is min(X1, X2).
sort_tas([X1, Y], X2, [S, Y], B):- !, B is max(X1, X2), S is min(X1, X2).
sort_tas([X1, Y, Z], X2, [S, Y, Z], B):- !, B is max(X1, X2), S is min(X1, X2).
