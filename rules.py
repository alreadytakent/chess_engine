import pygame


FPS = 60
DARK_COLOR = (140, 162, 173)
LIGHT_COLOR = (255, 255, 255)
COLORS = [LIGHT_COLOR, DARK_COLOR]
C = 80 # cell size


PIECE_IMAGES = {'bB': pygame.transform.smoothscale(pygame.image.load('piece_images/bB.png'), (C, C)), 
                'wB': pygame.transform.smoothscale(pygame.image.load('piece_images/wB.png'), (C, C)),
                'bK': pygame.transform.smoothscale(pygame.image.load('piece_images/bK.png'), (C, C)),
                'wK': pygame.transform.smoothscale(pygame.image.load('piece_images/wK.png'), (C, C)),
                'bN': pygame.transform.smoothscale(pygame.image.load('piece_images/bN.png'), (C, C)),
                'wN': pygame.transform.smoothscale(pygame.image.load('piece_images/wN.png'), (C, C)),
                'bP': pygame.transform.smoothscale(pygame.image.load('piece_images/bP.png'), (C, C)),
                'wP': pygame.transform.smoothscale(pygame.image.load('piece_images/wP.png'), (C, C)),
                'bQ': pygame.transform.smoothscale(pygame.image.load('piece_images/bQ.png'), (C, C)),
                'wQ': pygame.transform.smoothscale(pygame.image.load('piece_images/wQ.png'), (C, C)),
                'bR': pygame.transform.smoothscale(pygame.image.load('piece_images/bR.png'), (C, C)),
                'wR': pygame.transform.smoothscale(pygame.image.load('piece_images/wR.png'), (C, C))}


def is_on_board(coord):
    i = coord[0]
    j = coord[1]
    if i>0 and i<8 and j>0 and j<8:
        return True
    return False


class Chess:
    '''
    Содержит в себе информацию о состоянии самой игры
    '''
    def __init__(self, game_info):
        self.board = game_info[0]
        self.whose_turn = game_info[1]
        self.castling_possibilities = game_info[2]
        self.en_passant = game_info[3]
        self.draw_countdown = game_info[4]
        self.move_number = game_info[5]
    
    def show_board(self, screen):
        for i in range (0, 8):
            for j in range (0, 8):
                pygame.draw.rect(screen, COLORS[(i+j)%2], (i*C, j*C, C, C))
                if self.board[j][i] != '0':
                    screen.blit(self.board[j][i].image, (i*C, j*C))


class Board:
    '''
    Нужен для создания множества досок для поиска лучшего хода компьютером
    '''


class Piece:
    '''
    Создаёт фигуру, которая займёт место на доске
    '''


class Rook(Piece):
    
    def __init__(self, team, coord):
        self.team = team
        self.coord = coord
        self.image = PIECE_IMAGES[team+'R']
    
    def legal_moves(self, board):
        legal_moves = []
        I = self.coord[0]
        J = self.coord[1]
        for i in range (I+1, 8):
            if board[i][J] == '0':
                legal_moves.append((i, J))
            else:
                if board[i][J].team != self.team:
                    legal_moves.append((i, J))
                break
        for i in range (I-1, -1, -1):
            if board[i][J] == '0':
                legal_moves.append((i, J))
            else:
                if board[i][J].team != self.team:
                    legal_moves.append((i, J))
                break
        for j in range (J+1, 8):
            if board[I][j] == '0':
                legal_moves.append((I, j))
            else:
                if board[I][j].team != self.team:
                    legal_moves.append((I, j))
                break
        for j in range (J-1, -1, -1):
            if board[I][j] == '0':
                legal_moves.append((I, j))
            else:
                if board[I][j].team != self.team:
                    legal_moves.append((I, j))
                break
        yield legal_moves


class Bishop(Piece):
    
    def __init__(self, team, coord):
        self.team = team
        self.coord = coord
        self.image = PIECE_IMAGES[team+'B']
    
    def legal_moves(self, board):
        legal_moves = []
        I = self.coord[0]
        J = self.coord[1]
        for k in range (min(I, 7-J)):
            if board[I-k][J+k] == '0':
                legal_moves.append((I-k, J+k))
            else:
                if board[I-k][J+k].team != self.team:
                    legal_moves.append((I-k, J+k))
                break
        for k in range (min(I, J)):
            if board[I-k][J-k] == '0':
                legal_moves.append((I-k, J-k))
            else:
                if board[I-k][J-k].team != self.team:
                    legal_moves.append((I-k, J-k))
                break
        for k in range (min(7-I, J)):
            if board[I+k][J-k] == '0':
                legal_moves.append((I+k, J-k))
            else:
                if board[I+k][J-k].team != self.team:
                    legal_moves.append((I+k, J-k))
                break
        for k in range (min(7-I, 7-J)):
            if board[I+k][J+k] == '0':
                legal_moves.append((I+k, J+k))
            else:
                if board[I+k][J+k].team != self.team:
                    legal_moves.append((I+k, J+k))
                break
        yield legal_moves


class Knight(Piece):
    
    def __init__(self, team, coord):
        self.team = team
        self.coord = coord
        self.image = PIECE_IMAGES[team+'N']
    
    def legal_moves(self, board):
        legal_moves = []
        I = self.coord[0]
        J = self.coord[1]
        hypothetical_moves = [(I-1, J+2), (I-2, J+1), (I-2, J-1), (I-1, J-2), 
                              (I+1, J-2), (I+2, J-1), (I+2, J+1), (I+1, J+2)]
        for coord in hypothetical_moves:
            if is_on_board(coord):
                if board[coord[0]][coord[1]] == '0':
                    legal_moves.append(coord)
                elif board[coord[0]][coord[1]].team != self.team:
                    legal_moves.append(coord)
        yield legal_moves


class Pawn(Piece):
    
    def __init__(self, team, coord):
        self.team = team
        self.coord = coord
        self.image = PIECE_IMAGES[team+'P']
    
    def legal_moves(self, board):
        legal_moves = []
        I = self.coord[0]
        J = self.coord[1]
        if self.team == 'w':
            if board[I-1][J] == '0':
                legal_moves.append((I-1, J))
                if I == 6 and board[4][J] == '0':
                    legal_moves.append((4, J))
            if board[I-1][J-1] != '0':
                if board[I-1][J-1].team == 'b':
                    legal_moves.append((I-1, J-1))
            if board[I-1][J+1] != '0':
                if board[I-1][J+1].team == 'b':
                    legal_moves.append((I-1, J+1))
        else:
            if board[I+1][J] == '0':
                legal_moves.append((I+1, J))
                if I == 1 and board[3][J] == '0':
                    legal_moves.append((3, J))
            if board[I+1][J-1] != '0':
                if board[I+1][J-1].team == 'w':
                    legal_moves.append((I+1, J-1))
            if board[I+1][J+1] != '0':
                if board[I+1][J+1].team == 'w':
                    legal_moves.append((I+1, J+1))
        yield legal_moves


class Queen(Piece):
    
    def __init__(self, team, coord):
        self.team = team
        self.coord = coord
        self.image = PIECE_IMAGES[team+'Q']
    
    def legal_moves(self, board):
        ghost_rook = Rook(self.team, self.coord)
        ghost_bishop = Bishop(self.team, self.coord)
        legal_moves = [x for x in ghost_rook.legal_moves(board)]
        legal_moves.append(x for x in ghost_bishop.legal_moves(board))
        yield legal_moves


class King(Piece):
    
    def __init__(self, team, coord):
        self.team = team
        self.coord = coord
        self.image = PIECE_IMAGES[team+'K']
    
    def legal_moves(self, board):
        legal_moves = []
        I = self.coord[0]
        J = self.coord[1]
        hypothetical_moves = [(I, J+1), (I-1, J+1), (I-1, J), (I-1, J-1), 
                              (I, J-1), (I+1, J-1), (I+1, J), (I+1, J+1)]
        for coord in hypothetical_moves:
            if is_on_board(coord):
                if board[coord[0]][coord[1]] == '0':
                    legal_moves.append(coord)
                elif board[coord[0]][coord[1]].team != self.team:
                    legal_moves.append(coord)
        yield legal_moves
