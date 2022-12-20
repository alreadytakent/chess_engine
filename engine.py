from random import choice

engine_team = 1
b = (-1)**engine_team
w = -b
piece_values = {'p': 100*b, 'n': 300*b, 'b': 300*b, 'r': 500*b, 'q': 900*b, 'k': 0,
                'P': 100*w, 'N': 300*w, 'B': 300*w, 'R': 500*w, 'Q': 900*w, 'K': 0}

def engine_move(Board):
    possible_moves = [move for move in Board.legal_moves()]
    return choice(possible_moves)

def evaluate(Board):
    E = 0
    for piece in Board.pieces:
        E += piece_values[piece.label]
    return E
