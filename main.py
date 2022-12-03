"""
Created on Sat Dec  3 10:07:47 2022
"""

import pygame


FPS = 60
A1_COLOR = (140, 162, 173)
A2_COLOR = (255, 255, 255)
COLORS = [A2_COLOR, A1_COLOR]
C = 90 # cell size

piece_images = {'b': pygame.transform.smoothscale(pygame.image.load('piece_images/bB.png'), (C, C)), 
                'B': pygame.transform.smoothscale(pygame.image.load('piece_images/wB.png'), (C, C)),
                'k': pygame.transform.smoothscale(pygame.image.load('piece_images/bK.png'), (C, C)),
                'K': pygame.transform.smoothscale(pygame.image.load('piece_images/wK.png'), (C, C)),
                'n': pygame.transform.smoothscale(pygame.image.load('piece_images/bN.png'), (C, C)),
                'N': pygame.transform.smoothscale(pygame.image.load('piece_images/wN.png'), (C, C)),
                'p': pygame.transform.smoothscale(pygame.image.load('piece_images/bP.png'), (C, C)),
                'P': pygame.transform.smoothscale(pygame.image.load('piece_images/wP.png'), (C, C)),
                'q': pygame.transform.smoothscale(pygame.image.load('piece_images/bQ.png'), (C, C)),
                'Q': pygame.transform.smoothscale(pygame.image.load('piece_images/wQ.png'), (C, C)),
                'r': pygame.transform.smoothscale(pygame.image.load('piece_images/bR.png'), (C, C)),
                'R': pygame.transform.smoothscale(pygame.image.load('piece_images/wR.png'), (C, C))}

#Board = [['0' for i in range (8)] for i in range (8)]

starting_position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

Board = [['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
         ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
         ['0', '0', '0', '0', '0', '0', '0', '0'],
         ['0', '0', '0', '0', '0', '0', '0', '0'],
         ['0', '0', '0', '0', '0', '0', '0', '0'],
         ['0', '0', '0', '0', '0', '0', '0', '0'],
         ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
         ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']]



def print_board(board=Board):
    for i in range (8):
        print(*board[i])


def FEN_to_board(FEN):
    board_str, whose_turn, castling_possibilities, en_passant, draw_countdown, move_number = FEN.split()
    draw_countdown = int(draw_countdown)
    move_number = int(move_number)
    rows = list(board_str.split('/'))
    board = [['0' for i in range (8)] for i in range (8)]
    for i in range (8):
        j = 0
        for symbol in rows[i]:
            if symbol.isalpha():
                board[i][j] = symbol
                j += 1
            else:
                for k in range (int(symbol)):
                    board[i][j+k] = '0'
                j += int(symbol)    
    game_info = [board, whose_turn, castling_possibilities, en_passant, draw_countdown, move_number]
    return game_info

def board_to_FEN(game_info):
    board = game_info[0]
    FEN = ''
    for i in range (8):
        for j in range (8):
            k = 1
            if board[i][j] != '0':
                FEN += board[i][j]
            else:
                while j+k < 8 and board[i][j+k] == '0':
                    k += 1
                FEN += str(k)
        FEN += '/'
    return FEN


def show_board(screen, board=Board):
    for x in range (0, 8):
        for y in range (0, 8):
            pygame.draw.rect(screen, COLORS[(x+y)%2], (x*C, y*C, C, C))
            if board[y][x] != '0':
                screen.blit(piece_images[board[y][x]], (x*C, y*C))
    pass


def main(board=Board):
    finished = False
    pygame.init()
    screen = pygame.display.set_mode((C*8, C*8))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()
    while not finished:
        show_board(screen, FEN_to_board(starting_position)[0])
        clock.tick(FPS)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
    pygame.quit()

main()