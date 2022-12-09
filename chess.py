import pygame


starting_position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

FPS = 60
DARK_COLOR = (140, 162, 173)
LIGHT_COLOR = (255, 255, 255)
GREEN = (0, 255, 0)
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
    '''coord = (i, j)'''
    i = coord[0]
    j = coord[1]
    if i>=0 and i<8 and j>=0 and j<8:
        return True
    return False


def FEN_to_board(FEN):
    '''Конвертирует строку FEN в список, из которого проще достать нужную информацию об игре'''
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


def print_board(board):
    print('================')
    for row in board:
        string = ''
        for square in row:
            if square == '0':
                string += '. '
            else:
                if square.team == 'w':
                    string += square.__class__.__name__ + ' '
                else:
                    string += square.__class__.__name__.lower() + ' '
        print(string, end='\n')
    print('================')
    pass


def create_piece(label, coord):
    if label.isupper():
        team = 'w'
        label = label.lower()
    else:
        team = 'b'
    if label == 'b':
        return B(team, coord)
    elif label == 'k':
        return K(team, coord)
    elif label == 'r':
        return R(team, coord)
    elif label == 'p':
        return P(team, coord)
    elif label == 'n':
        return N(team, coord)
    elif label == 'q':
        return Q(team, coord)


class Chess:
    '''
    Содержит в себе информацию о состоянии самой игры
    '''
    def __init__(self, FEN):
        '''Принимает строку в формате FEN'''
        self.game = Board(FEN_to_board(FEN))
        self.grabbed_piece = '0'
        self.highlight = True
    
    def show_board(self, screen):
        for i in range (0, 8):
            for j in range (0, 8):
                pygame.draw.rect(screen, COLORS[(i+j)%2], (i*C, j*C, C, C))
    
    def show_pieces(self, screen):
        for piece in self.game.pieces:
            piece.show_yourself(screen)
    
    def show_grabbed_piece(self, screen, pos):
        if self.grabbed_piece != '0':
            screen.blit(self.grabbed_piece.image, pos)
    
    def show_legal_moves(self, screen, piece):
        if self.highlight and piece != '0':
            for coord in piece.legal_moves(self.game.board):
                pygame.draw.circle(screen, GREEN, (coord[1]*C + C//2, coord[0]*C + C//2), C*2//5)
    
    def grab_piece(self, i, j):
        '''Просто копирует фигуру с доски в руку'''
        if self.game.board[i][j] != '0':
            self.grabbed_piece = self.game.board[i][j]
            self.grabbed_piece.visible = False
    
    
    def drop_piece(self, i, j):
        '''
        Сценарий --- Действия
        1. Фигура не сдвинулась с места --- Очистить руку. Доска не меняется. Ход не делается.
        2. Фигура сдвинулась на непустое поле --- Если это фигура-союзник - очистить руку. Доска не меняется. Ход не делается.
        3. Фигура сдвинулась на непустое поле --- Если это фигура противника - убрать её с доски. Осуществить ход:
                                                Очистить бывшую клетку сдвинувшейся фигуры. Присвоить новые координаты фигуре в руке.                       
        '''
        if not (i, j) in self.grabbed_piece.legal_moves(self.game.board):
            self.grabbed_piece.visible = True
            self.grabbed_piece = '0'
        
        elif self.game.board[i][j] != '0':
            if self.game.board[i][j].team == self.grabbed_piece.team:
                self.grabbed_piece.visible = True
                self.grabbed_piece = '0'
            else:
                self.game.board[self.grabbed_piece.coord[0]][self.grabbed_piece.coord[1]] = '0'
                self.grabbed_piece.visible = True
                self.game.remove_piece(i, j)
                self.grabbed_piece.coord = (i, j)
                self.game.board[i][j] = self.grabbed_piece
                self.grabbed_piece = '0'
                self.game.change_turn()
        else:
            self.game.board[self.grabbed_piece.coord[0]][self.grabbed_piece.coord[1]] = '0'
            self.grabbed_piece.visible = True
            self.grabbed_piece.coord = (i, j)
            self.game.board[i][j] = self.grabbed_piece
            self.grabbed_piece = '0'
            self.game.change_turn()


class Board:
    '''
    Нужен для создания множества досок для поиска лучшего хода компьютером
    '''
    def __init__(self, game_info):
        self.board = game_info[0]
        self.whose_turn = game_info[1]
        self.castling_possibilities = game_info[2]
        self.en_passant = game_info[3]
        self.draw_countdown = game_info[4]
        self.move_number = game_info[5]
        self.pieces = []
        for i in range (8):
            for j in range (8):
                if self.board[i][j] != '0':
                    new_piece = create_piece(self.board[i][j], (i, j))
                    self.board[i][j] = new_piece
                    self.pieces.append(new_piece)
    
    def remove_piece(self, i, j):
        for piece in self.pieces:
            if piece.coord == (i, j):
                self.pieces.remove(piece)
    
    def change_turn(self):
        if self.whose_turn == 'w':
            self.whose_turn = 'b'
        else:
            self.whose_turn = 'w'


class Piece:
    
    def __init__(self, label):
        
        pass
    '''
    Создаёт фигуру, которая займёт место на доске
    '''


class R(Piece):
    
    def __init__(self, team, coord):
        self.team = team
        self.coord = coord
        self.image = PIECE_IMAGES[team+'R']
        self.visible = True
    
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
        return legal_moves
    
    def show_yourself(self, screen):
        if self.visible:
            screen.blit(self.image, (self.coord[1]*C, self.coord[0]*C))


class B(Piece):
    
    def __init__(self, team, coord):
        self.team = team
        self.coord = coord
        self.image = PIECE_IMAGES[team+'B']
        self.visible = True
    
    def legal_moves(self, board):
        legal_moves = []
        I = self.coord[0]
        J = self.coord[1]
        for k in range (min(I, 7-J)):
            k += 1
            if board[I-k][J+k] == '0':
                legal_moves.append((I-k, J+k))
            else:
                if board[I-k][J+k].team != self.team:
                    legal_moves.append((I-k, J+k))
                break
        for k in range (min(I, J)):
            k += 1
            if board[I-k][J-k] == '0':
                legal_moves.append((I-k, J-k))
            else:
                if board[I-k][J-k].team != self.team:
                    legal_moves.append((I-k, J-k))
                break
        for k in range (min(7-I, J)):
            k += 1
            if board[I+k][J-k] == '0':
                legal_moves.append((I+k, J-k))
            else:
                if board[I+k][J-k].team != self.team:
                    legal_moves.append((I+k, J-k))
                break
        for k in range (min(7-I, 7-J)):
            k += 1
            if board[I+k][J+k] == '0':
                legal_moves.append((I+k, J+k))
            else:
                if board[I+k][J+k].team != self.team:
                    legal_moves.append((I+k, J+k))
                break
        return legal_moves
    
    def show_yourself(self, screen):
        if self.visible:
            screen.blit(self.image, (self.coord[1]*C, self.coord[0]*C))


class N(Piece):
    
    def __init__(self, team, coord):
        self.team = team
        self.coord = coord
        self.image = PIECE_IMAGES[team+'N']
        self.visible = True
    
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
        return legal_moves
    
    def show_yourself(self, screen):
        if self.visible:
            screen.blit(self.image, (self.coord[1]*C, self.coord[0]*C))


class P(Piece):
    
    def __init__(self, team, coord):
        self.team = team
        self.coord = coord
        self.image = PIECE_IMAGES[team+'P']
        self.visible = True
    
    def legal_moves(self, board):
        legal_moves = []
        I = self.coord[0]
        J = self.coord[1]
        if self.team == 'w':
            if board[I-1][J] == '0':
                legal_moves.append((I-1, J))
                if I == 6 and board[4][J] == '0':
                    legal_moves.append((4, J))
            if is_on_board((I-1, J-1)) and board[I-1][J-1] != '0':
                if board[I-1][J-1].team == 'b':
                    legal_moves.append((I-1, J-1))
            if is_on_board((I-1, J+1)) and board[I-1][J+1] != '0':
                if board[I-1][J+1].team == 'b':
                    legal_moves.append((I-1, J+1))
        else:
            if board[I+1][J] == '0':
                legal_moves.append((I+1, J))
                if I == 1 and board[3][J] == '0':
                    legal_moves.append((3, J))
            if is_on_board((I+1, J-1)) and board[I+1][J-1] != '0':
                if board[I+1][J-1].team == 'w':
                    legal_moves.append((I+1, J-1))
            if is_on_board((I+1, J+1)) and board[I+1][J+1] != '0':
                if board[I+1][J+1].team == 'w':
                    legal_moves.append((I+1, J+1))
        return legal_moves
    
    def show_yourself(self, screen):
        if self.visible:
            screen.blit(self.image, (self.coord[1]*C, self.coord[0]*C))


class Q(Piece):
    
    def __init__(self, team, coord):
        self.team = team
        self.coord = coord
        self.image = PIECE_IMAGES[team+'Q']
        self.visible = True
    
    def legal_moves(self, board):
        ghost_rook = R(self.team, self.coord)
        ghost_bishop = B(self.team, self.coord)
        legal_moves = [x for x in ghost_rook.legal_moves(board)]
        legal_moves += [x for x in ghost_bishop.legal_moves(board)]
        return legal_moves
    
    def show_yourself(self, screen):
        if self.visible:
            screen.blit(self.image, (self.coord[1]*C, self.coord[0]*C))


class K(Piece):
    
    def __init__(self, team, coord):
        self.team = team
        self.coord = coord
        self.image = PIECE_IMAGES[team+'K']
        self.visible = True
    
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
        return legal_moves
    
    def show_yourself(self, screen):
        if self.visible:
            screen.blit(self.image, (self.coord[1]*C, self.coord[0]*C))


def main(starting_position):
    
    finished = False
    pygame.init()
    screen = pygame.display.set_mode((C*8, C*8))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()
    
    chess = Chess(starting_position)
    
    while not finished:
        
        pos = pygame.mouse.get_pos()
        chess.show_board(screen)
        chess.show_pieces(screen)
        chess.show_grabbed_piece(screen, (pos[0]-C//2, pos[1]-C//2))
        chess.show_legal_moves(screen, chess.grabbed_piece)
        
        clock.tick(FPS)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                i, j = pos[1]//C, pos[0]//C
                if chess.game.board[i][j] != '0' and chess.game.board[i][j].team == chess.game.whose_turn:
                    chess.grab_piece(i, j)
            elif event.type == pygame.MOUSEBUTTONUP and chess.grabbed_piece != '0':
                chess.drop_piece(pos[1]//C, pos[0]//C)
                
    pygame.quit()
    pass

main(starting_position)











