import pygame
from engine import engine_move

start_pos = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

FPS = 60
C = 80
L, R, U, D = (0.5*C, 0.5*C, 0.5*C, 0.5*C)

DARK_COLOR = (140, 162, 173)
LIGHT_COLOR = (255, 255, 255)
COLORS = [LIGHT_COLOR, DARK_COLOR]

HIGHLIGHTED_DARK_COLOR = (140, 200, 173)
HIGHLIGHTED_LIGHT_COLOR = (200, 255, 200)
HIGHLIGHTED_COLORS = [HIGHLIGHTED_LIGHT_COLOR, HIGHLIGHTED_DARK_COLOR]

RED = (255, 0, 0)
BACKGROUND_COLOR = (100, 100, 100)

AUTOQUEEN = True

def print_board(board):
    print('================')
    for row in board:
        string = ''
        for square in row:
            if square.empty:
                string += '. '
            else:
                string += square.label + ' '
        print(string, end='\n')
    print('================')

def FEN_to_info(FEN):
    """
    Возращает по FEN информацию о доске: массив, характеризующий позицию 
    на доске, чей ход, возможна ли рокировка,  можно ли брать на проходе.
    """
    board_str, whose_turn, castling, en_passant, draw_countdown, move_number = FEN.split()
    if whose_turn == 'w':
        whose_turn = 1
    else:
        whose_turn = 0
    if castling == '-':
        castling = ''
    if en_passant == '-':
        en_passant = -2
    draw_countdown = int(draw_countdown)
    move_number = int(move_number)
    rows = list(board_str.split('/'))
    board = [[0 for i in range (8)] for i in range (8)]
    for i in range (8):
        j = 0
        for symbol in rows[i]:
            if symbol.isalpha():
                board[i][j] = create_piece(symbol, (i, j))
                j += 1
            else:
                for k in range (int(symbol)):
                    board[i][j+k] = Square()
                j += int(symbol)    
    return [board, whose_turn, castling, en_passant]


def load_image(s):
    return pygame.transform.smoothscale(pygame.image.load('piece_images/' + s + '.png'), (C, C))


def isonboard(coord):
    """Проверяем являются ли коорбинаты, координатами доски"""
    i, j = coord
    if (i > -1) & (i < 8) & (j > -1) & (j < 8):
        return True
    return False


def create_piece(label, coord):
    u = label.lower()
    if u == 'p':
        return Pawn(label, coord)
    elif u == 'n':
        return Knight(label, coord)
    elif u == 'b':
        return Bishop(label, coord)
    elif u == 'r':
        return Rook(label, coord)
    elif u == 'q':
        return Queen(label, coord)
    elif u == 'k':
        return King(label, coord)
    else:
        raise TypeError('Incorrect piece label')


def isattacked(board, team, coord):
    """ Возвращает атакована ли клетка. """
    io, jo = coord
    piece_labels = [['P', 'N', 'B', 'Q', 'R', 'K'], ['p', 'n', 'b', 'q', 'r', 'k']][team]
    king_attacks = [(io, jo+1), (io-1, jo+1), (io-1, jo), (io-1, jo-1),
                    (io, jo-1), (io+1, jo-1), (io+1, jo), (io+1, jo+1)]
    for coord in king_attacks:
        if isonboard(coord):
            square = board[coord[0]][coord[1]]
            if not square.empty and square.label == piece_labels[5]:
                return True
    pawn_attacks = [[(io+1, jo-1), (io+1, jo+1)], [(io-1, jo-1), (io-1, jo+1)]][team]
    for coord in pawn_attacks:
        if isonboard(coord):
            square = board[coord[0]][coord[1]]
            if not square.empty and square.label == piece_labels[0]:
                return True
    knight_attacks = [(io-1, jo+2), (io-2, jo+1), (io-2, jo-1), (io-1, jo-2),
                      (io+1, jo-2), (io+2, jo-1), (io+2, jo+1), (io+1, jo+2)]
    for coord in knight_attacks:
        if isonboard(coord):
            square = board[coord[0]][coord[1]]
            if not square.empty and square.label == piece_labels[1]:
                return True
    lines = [[(io, k) for k in range (jo+1, 8)],
            [(k, jo) for k in range (io-1, -1, -1)],
            [(io, k) for k in range (jo-1, -1, -1)],
            [(k, jo) for k in range (io+1, 8)]]
    for line in lines:
        for coord in line:
            square = board[coord[0]][coord[1]]
            if not square.empty:
                if square.label in piece_labels[3:5]:
                    return True
                break
    diags = [[(io-k, jo+k) for k in range (1, min(io, 7-jo)+1)],
             [(io-k, jo-k) for k in range (1, min(io, jo)+1)],
             [(io+k, jo-k) for k in range (1, min(7-io, jo)+1)],
             [(io+k, jo+k) for k in range (1, min(7-io, 7-jo)+1)]]
    for diag in diags:
        for coord in diag:
            square = board[coord[0]][coord[1]]
            if not square.empty:
                if square.label in piece_labels[2:4]:
                    return True
                break
    return False


def pawn_promote(coord):
    """Возвращаем фигуру, на которую надо поменять пешку, которая дошла до края"""
    if coord[0] == 0:
        team = 1
    else:
        team = 0
    if AUTOQUEEN:
        return create_piece(['q', 'Q'][team], coord)
    label = input()
    return create_piece(label, coord)


class Square:
    """Класс клетки"""
    def __init__(self):
        self.empty = 1


class Piece:
    
    def __init__(self, label, coord):
        self.empty = 0
        self.label = label
        self.coord = coord
        self.team = label.isupper()
        self.image = load_image(['b', 'w'][self.team] + label.upper())
        self.visible = 1
    
    def show_yourself(self, screen, reverse):
        """
        Выводим фигуру на экран.
        reverse[True|False] - дооска перевернута|не перевернута
        """
        if self.visible:
            if reverse:
                screen.blit(self.image, (L + (7-self.coord[1])*C, U + (7-self.coord[0])*C))
            else:
                screen.blit(self.image, (L + self.coord[1]*C, U + self.coord[0]*C))


class Pawn(Piece):
    """Описывает ходы пешки"""
    
    def __init__(self, label, coord):
        super().__init__(label, coord)
    
    def legal_moves(self, Board):
        io, jo = self.coord
        board = Board.board
        king = Board.kings[self.team]
        en_passant = Board.en_passant
        def move_inspector(coord):
            return not isattacked(Board.move(self.coord, coord), self.team, king.coord)
        legal_moves = []
        starting_row = [1, 6][self.team]
        step = (-1)**self.team
        i = io+step
        if (i > -1) & (i < 8):
            if board[i][jo].empty:
                if move_inspector((i, jo)):
                    legal_moves.append((i, jo))
                if io == starting_row and board[i+step][jo].empty:
                    if move_inspector((i+step, jo)):
                        legal_moves.append((i+step, jo))
            for j in (jo-1, jo+1):
                if ((j > -1) & (j < 8)) and not board[i][j].empty and (board[i][j].team ^ self.team):
                    if move_inspector((i, j)):
                        legal_moves.append((i, j))
        if io == starting_row + 3*step and abs(jo-en_passant) == 1:
            if not isattacked(Board.move(self.coord, (i, en_passant)), self.team, king.coord):
                    legal_moves.append((i, en_passant))
        return legal_moves


class Knight(Piece):
    """Описывает ходы коня"""
    
    def __init__(self, label, coord):
        super().__init__(label, coord)
    
    def legal_moves(self, Board):
        io, jo = self.coord
        board = Board.board
        king = Board.kings[self.team]
        def move_inspector(coord):
            return not isattacked(Board.move(self.coord, coord), self.team, king.coord)
        legal_moves = []
        knight_moves = [(io-1, jo+2), (io-2, jo+1), (io-2, jo-1), (io-1, jo-2),
                        (io+1, jo-2), (io+2, jo-1), (io+2, jo+1), (io+1, jo+2)]
        for coord in knight_moves:
            if isonboard(coord):
                i, j = coord
                if board[i][j].empty or (board[i][j].team ^ self.team):
                    if move_inspector(coord):
                        legal_moves.append(coord)
        return legal_moves


class Bishop(Piece):
    """Описывает ходы слона"""
    
    def __init__(self, label, coord):
        super().__init__(label, coord)
    
    def legal_moves(self, Board):
        io, jo = self.coord
        board = Board.board
        king = Board.kings[self.team]
        def move_inspector(coord):
            return not isattacked(Board.move(self.coord, coord), self.team, king.coord)
        legal_moves = []
        diags = [[(io-k, jo+k) for k in range (1, min(io, 7-jo)+1)],
                 [(io-k, jo-k) for k in range (1, min(io, jo)+1)],
                 [(io+k, jo-k) for k in range (1, min(7-io, jo)+1)],
                 [(io+k, jo+k) for k in range (1, min(7-io, 7-jo)+1)]]
        for diag in diags:
            for coord in diag:
                square = board[coord[0]][coord[1]]
                if square.empty:
                    if move_inspector(coord):
                        legal_moves.append(coord)
                else: 
                    if square.team ^ self.team:
                        if move_inspector(coord):
                            legal_moves.append(coord)
                    break
        return legal_moves


class Rook(Piece):
    """Описывает ходы ладьи"""
    
    def __init__(self, label, coord):
        super().__init__(label, coord)
    
    def legal_moves(self, Board):
        io, jo = self.coord
        board = Board.board
        king = Board.kings[self.team]
        def move_inspector(coord):
            return not isattacked(Board.move(self.coord, coord), self.team, king.coord)
        legal_moves = []
        lines = [[(io, k) for k in range (jo+1, 8)],
                 [(k, jo) for k in range (io-1, -1, -1)],
                 [(io, k) for k in range (jo-1, -1, -1)],
                 [(k, jo) for k in range (io+1, 8)]]
        for line in lines:
            for coord in line:
                square = board[coord[0]][coord[1]]
                if square.empty:
                    if move_inspector(coord):
                        legal_moves.append(coord)
                else: 
                    if square.team ^ self.team:
                        if move_inspector(coord):
                            legal_moves.append(coord)
                    break
        return legal_moves


class Queen(Piece):
    """Описывает ходы ферзя"""
    
    def __init__(self, label, coord):
        super().__init__(label, coord)
    
    def legal_moves(self, Board):
        ghost_rook = Rook(['r', 'R'][self.team], self.coord)
        ghost_bishop = Bishop(['b', 'B'][self.team], self.coord)
        return ghost_rook.legal_moves(Board) + ghost_bishop.legal_moves(Board)


class King(Piece):
    """Описывает ходы короля"""
    
    def __init__(self, label, coord):
        super().__init__(label, coord)
        self.w = [0, 7][self.team]
    
    def legal_moves(self, Board):
        io, jo = self.coord
        board = Board.board
        castling = Board.castling
        legal_moves = []
        king_moves = [(io, jo+1), (io-1, jo+1), (io-1, jo), (io-1, jo-1),
                      (io, jo-1), (io+1, jo-1), (io+1, jo), (io+1, jo+1)]
        for coord in king_moves:
            if isonboard(coord):
                square = board[coord[0]][coord[1]]
                if square.empty or (square.team ^ self.team):
                    if not isattacked(Board.move(self.coord, coord), self.team, coord):
                        legal_moves.append(coord)
        if not Board.check:
            for c in castling:
                if c == ['k', 'K'][self.team]:
                    s = True
                    for j in [5, 6]:
                        if not board[self.w][j].empty or isattacked(board, self.team, (self.w, j)):
                            s = False
                            break
                    if s:
                        legal_moves.append((self.w, 6))
                elif c == ['q', 'Q'][self.team]:
                    s = True
                    for j in [1, 2, 3]:
                        if not board[self.w][j].empty or isattacked(board, self.team, (self.w, j)):
                            s = False
                            break
                    if s:
                        legal_moves.append((self.w, 2))
        return legal_moves


class Board:
    """Описывает действия, происходящие на доске"""
    
    def __init__(self, info):
        self.board = info[0]
        self.turn = info[1]
        self.castling = info[2]
        self.en_passant = info[3]
        self.check = 0
        self.pieces = []
        self.kings = [None, None]
        for i in range (8):
            for j in range (8):
                square = self.board[i][j]
                if not square.empty:
                    self.pieces.append(square)
                    if square.label == 'K':
                        self.kings[1] = square
                    elif square.label == 'k':
                        self.kings[0] = square
    
    def legal_moves(self):
        for piece in self.pieces:
            if not (piece.team ^ self.turn):
                for coord in piece.legal_moves(self):
                    yield [piece.coord, coord]
    
    def termination(self):
        """Проверка на мат и пат, завершение игры"""
        end = True
        if len(self.pieces) == 2:
            print('Draw by insufficient material')
            return end
        for piece in self.pieces:
            if piece.team == self.turn:
                if piece.legal_moves(self) != []:
                    end = False
        if end:
            if self.check:
                print('Checkmate')
            else:
                print('Stalemate')
        return end

    def remove_piece(self, coord):
        i, j = coord
        self.pieces.remove(self.board[i][j])
    
    def change_turn(self):
        self.turn = 1 - self.turn
    
    def move(self, start, end):
        """Возвращает доску после сделанного хода"""
        piece = self.board[start[0]][start[1]]
        board_copy = [row[:] for row in self.board]
        board_copy[start[0]][start[1]] = Square()
        board_copy[end[0]][end[1]] = piece
        return board_copy
    
    def push(self, start, end):
        """Характеризует ход и доску: проверка на мат, шах, пат, рокировку, взятие на проходе"""
        io, jo = start
        i, j = end
        piece = self.board[io][jo]
        piece.coord = end
        square = self.board[i][j]
        if not square.empty:
            self.pieces.remove(square)
        label = piece.label
        team = piece.team
        en_passant = -2
        self.board = self.move(start, end)
        if label == ['p', 'P'][team]:
            if abs(i-io) == 2:
                en_passant = j 
            elif i == [7, 0][team]:
                new_piece = pawn_promote((i, j))
                self.board[i][j] = new_piece
                self.pieces.remove(piece)
                self.pieces.append(new_piece)
            elif j == self.en_passant and i == [5, 2][team]:
                self.pieces.remove(self.board[[4, 3][team]][j])
                self.board[[4, 3][team]][j] = Square()
        elif label == ['k', 'K'][team] and self.castling != '':
            w = piece.w
            d = start[1] - end[1]
            if d == 2:
                rook = self.board[w][0]
                rook.coord = (w, 3)
                self.board[w][3] = rook
                self.board[w][0] = Square()
                for c in self.castling:
                    if c in [['k', 'q'], ['K', 'Q']][team]:
                        self.castling = self.castling.replace(c, '')
            elif d == -2:
                rook = self.board[w][7]
                rook.coord = (w, 5)
                self.board[w][5] = rook
                self.board[w][7] = Square()
                for c in self.castling:
                    if c in [['k', 'q'], ['K', 'Q']][team]:
                        self.castling = self.castling.replace(c, '')
            else:
                for c in self.castling:
                    if c in [['k', 'q'], ['K', 'Q']][team]:
                        self.castling = self.castling.replace(c, '')
        elif label == ['r', 'R'][team] and self.castling != '':
            if j == 0:
                h = ['q', 'Q'][team]
            else:
                h = ['k', 'K'][team]
            self.castling = self.castling.replace(h, '')
        self.en_passant = en_passant
        self.change_turn()
        if isattacked(self.board, self.turn, self.kings[self.turn].coord):
            self.check = 1
        else:
            self.check = 0


class Chess:
    """Вывод самих шахмат на экран"""
    
    def __init__(self, FEN, players):
        self.game = Board(FEN_to_info(FEN))
        self.grabbed_piece = Square()
        self.highlighted_moves = []
        self.reverse = 0
        player0, player1 = players
        if player0 == 'human':
            if player1 == 'bot':
                self.mode = 0
                self.engine_team = 1
            else:
                self.mode = 1
        elif player1 == 'human':
            self.mode = 0
            self.engine_team = 0
        else:
            self.mode = 2
                
    
    def rotate_board(self):
        """Поворот доски"""
        self.reverse = 1 - self.reverse
    
    def show_board(self, screen):
        """Выводит доску на экран"""
        for i in range (8):
            for j in range (8):
                pygame.draw.rect(screen, COLORS[(i+j)%2], (L + i*C, U + j*C, C, C))
    
    def show_pieces(self, screen):
        """Выводит фигуры на экран"""
        for piece in self.game.pieces:
            piece.show_yourself(screen, self.reverse)
    
    def show_grabbed_piece(self, screen, pos):
        """Захваченные фигуры движутся вместе с курсором"""
        if not self.grabbed_piece.empty:
            screen.blit(self.grabbed_piece.image, pos)
    
    def show_legal_moves(self, screen):
        """Подсвечивает клетки на которые может сходить захваченная фигура"""
        for coord in self.highlighted_moves:
            i, j = coord
            if self.reverse:
                i, j = 7-i, 7-j
            pygame.draw.rect(screen, HIGHLIGHTED_COLORS[(i+j)%2], (L + j*C, U + i*C, C, C))
    
    def show_check(self, screen):
        if self.game.check:
            i, j = self.game.kings[self.game.turn].coord
            if self.reverse:
                pygame.draw.rect(screen, RED, (L + (7-j)*C, U + (7-i)*C, C, C))
            else:
                pygame.draw.rect(screen, RED, (L + j*C, U + i*C, C, C))
            

    def grab_piece(self, i, j):
        """Действия, которые совершаются после взятия фигуры"""
        if self.reverse:
            i, j = 7-i, 7-j
        square = self.game.board[i][j]
        if not (square.empty or (square.team ^ self.game.turn)):
            square.visible = 0
            self.grabbed_piece = square
            self.highlighted_moves = square.legal_moves(self.game)
    
    def drop_piece(self, i, j):
        """Действия, которые совершаются после отпускания фигуры"""
        self.grabbed_piece.visible = 1
        if self.reverse:
            i, j = 7-i, 7-j
        if (i, j) in self.highlighted_moves:
            self.push((self.grabbed_piece.coord, (i, j)))
            pygame.display.update()
        self.grabbed_piece = Square()
        self.highlighted_moves = []
    
    def push(self, move):
        start, end = move
        self.game.push(start, end) 


def play(players):
    finished = False
    pygame.init()
    screen = pygame.display.set_mode((L + C*8 + R, U + C*8 + D))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()
    chess = Chess(start_pos, players)
    if chess.mode == 2:
        while not (finished or chess.game.termination()):
            chess.push(engine_move(chess.game))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finished = True
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                    chess.rotate_board()
            screen.fill(BACKGROUND_COLOR)
            chess.show_board(screen)
            chess.show_check(screen)
            chess.show_pieces(screen)
            clock.tick(FPS)
            pygame.display.update()
        while not finished:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finished = True
    elif chess.mode == 1:
        while not (finished or chess.game.termination()):
            pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finished = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    i, j = (int((pos[1]-U)//C), int((pos[0]-L)//C))
                    if isonboard((i, j)):
                        chess.grab_piece(i, j)
                elif event.type == pygame.MOUSEBUTTONUP:
                    i, j = (int((pos[1]-U)//C), int((pos[0]-L)//C))
                    if isonboard((i, j)):
                        chess.drop_piece(i, j)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                    chess.rotate_board()
            screen.fill(BACKGROUND_COLOR)
            chess.show_board(screen)
            chess.show_legal_moves(screen)
            chess.show_check(screen)
            chess.show_pieces(screen)
            chess.show_grabbed_piece(screen, (pos[0]-C//2, pos[1]-C//2))
            clock.tick(FPS)
            pygame.display.update()
        while not finished:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finished = True
    else:
        print(chess.engine_team)
        if not (chess.game.turn ^ chess.engine_team):
            if not chess.game.termination():
                chess.push(engine_move(chess.game))
        while not finished:
            pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    finished = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    i, j = (int((pos[1]-U)//C), int((pos[0]-L)//C))
                    if isonboard((i, j)):
                        chess.grab_piece(i, j)
                elif event.type == pygame.MOUSEBUTTONUP:
                    i, j = (int((pos[1]-U)//C), int((pos[0]-L)//C))
                    if isonboard((i, j)):
                        chess.drop_piece(i, j)
                        if not (chess.game.turn ^ chess.engine_team):
                            if not chess.game.termination():
                                chess.push(engine_move(chess.game))
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                    chess.rotate_board()
            screen.fill(BACKGROUND_COLOR)
            chess.show_board(screen)
            chess.show_legal_moves(screen)
            chess.show_check(screen)
            chess.show_pieces(screen)
            chess.show_grabbed_piece(screen, (pos[0]-C//2, pos[1]-C//2))
            clock.tick(FPS)
            pygame.display.update()
    pygame.quit()
