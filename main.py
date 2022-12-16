import pygame

FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

FPS = 60
C = 80

DARK_COLOR = (140, 162, 173)
LIGHT_COLOR = (255, 255, 255)
COLORS = [LIGHT_COLOR, DARK_COLOR]

HIGHLIGHTED_DARK_COLOR = (140, 200, 173)
HIGHLIGHTED_LIGHT_COLOR = ((200, 255, 200))
HIGHLIGHTED_COLORS = [HIGHLIGHTED_DARK_COLOR, HIGHLIGHTED_LIGHT_COLOR]


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
    pass


def FEN_to_info(FEN):
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


def pawn_promote():
    pass


class Square:
    
    def __init__(self):
        self.empty = 1


class Piece:
    
    def __init__(self, label, coord):
        self.empty = 0
        self.label = label
        self.coord = coord
        self.team = label.isupper()
        self.image = load_image(['b', 'w'][self.team] + label.upper())
    
    def show_yourself(self, screen, reverse):
        if reverse:
            screen.blit(self.image, ((7-self.coord[1])*C, (7-self.coord[0])*C))
        else:
            screen.blit(self.image, (self.coord[1]*C, self.coord[0]*C))


class Pawn(Piece):
    
    def __init__(self, label, coord):
        super().__init__(label, coord)
    
    def legal_moves(self, Board):
        io, jo = self.coord
        board = Board.board
        king = Board.kings[self.team]
        en_passant = Board.en_passant
        def move_inspector(coord):
            return not isattacked(Board.move(self.coord, coord), self.team, king.coord)
        '''
        if Board.check:
            def move_inspector(coord):
                return not isattacked(Board.move(self.coord, coord), self.team, king.coord)
        else:
            board_copy = [row[:] for row in board]
            board_copy[io][jo] = Square()
            if isattacked(board_copy, self.team, king.coord):
                return []
            def move_inspector(coord):
                return True
        '''
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
    
    def __init__(self, label, coord):
        super().__init__(label, coord)
    
    def legal_moves(self, Board):
        io, jo = self.coord
        board = Board.board
        king = Board.kings[self.team]
        def move_inspector(coord):
            return not isattacked(Board.move(self.coord, coord), self.team, king.coord)
        '''
        if Board.check:
            def move_inspector(coord):
                return not isattacked(Board.move(self.coord, coord), self.team, king.coord)
        else:
            board_copy = [row[:] for row in board]
            board_copy[io][jo] = Square()
            if isattacked(board_copy, self.team, king.coord):
                return []
            def move_inspector(coord):
                return True
        '''
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
    
    def __init__(self, label, coord):
        super().__init__(label, coord)
    
    def legal_moves(self, Board):
        io, jo = self.coord
        board = Board.board
        king = Board.kings[self.team]
        def move_inspector(coord):
            return not isattacked(Board.move(self.coord, coord), self.team, king.coord)
        '''
        if Board.check:
            def move_inspector(coord):
                return not isattacked(Board.move(self.coord, coord), self.team, king.coord)
        else:
            board_copy = [row[:] for row in board]
            board_copy[io][jo] = Square()
            if isattacked(board_copy, self.team, king.coord):
                return []
            def move_inspector(coord):
                return True
        '''
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
    
    def __init__(self, label, coord):
        super().__init__(label, coord)
    
    def legal_moves(self, Board):
        io, jo = self.coord
        board = Board.board
        king = Board.kings[self.team]
        def move_inspector(coord):
            return not isattacked(Board.move(self.coord, coord), self.team, king.coord)
        '''
        if Board.check:
            def move_inspector(coord):
                return not isattacked(Board.move(self.coord, coord), self.team, king.coord)
        else:
            board_copy = [row[:] for row in board]
            board_copy[io][jo] = Square()
            if isattacked(board_copy, self.team, king.coord):
                return []
            def move_inspector(coord):
                return True
        '''
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
    
    def __init__(self, label, coord):
        super().__init__(label, coord)
    
    def legal_moves(self, Board):
        ghost_rook = Rook(['r', 'R'][self.team], self.coord)
        ghost_bishop = Bishop(['b', 'B'][self.team], self.coord)
        return ghost_rook.legal_moves(Board) + ghost_bishop.legal_moves(Board)


class King(Piece):
    
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
        legal_moves = []
        for piece in self.pieces:
            legal_moves.append(piece.legal_moves(self.info))
    
    def remove_piece(self, coord):
        i, j = coord
        self.pieces.remove(self.board[i][j])
    
    def change_turn(self):
        self.turn = 1 - self.turn
    
    def move(self, start, end):
        piece = self.board[start[0]][start[1]]
        board_copy = [row[:] for row in self.board]
        board_copy[start[0]][start[1]] = Square()
        board_copy[end[0]][end[1]] = piece
        return board_copy
    
    def push(self, start, end):
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
                self.board[i][j] = pawn_promote()
            elif j == self.en_passant and i == [5, 2][team]:
                self.pieces.remove(self.board[[4, 3][team]][j])
                self.board[[4, 3][team]][j] = Square()
        elif label == ['k', 'K'][team] and len(self.castling) != 0:
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
                self.castling = []
        elif label == ['r', 'R'][team] and len(self.castling) != 0:
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
    
    def __init__(self, start_pos):
        self.game = Board(FEN_to_info(FEN))
        self.grabbed_piece = Square()
        self.highlighted_moves = []
        self.reverse = 0
    
    def rotate_board(self):
        self.reverse = 1 - self.reverse
    
    def show_board(self, screen):
        if self.reverse:
            for i in range (8):
                for j in range (8):
                    pygame.draw.rect(screen, COLORS[(i+j)%2], ((7-i)*C, (7-j)*C, C, C))
        else:
            for i in range (8):
                for j in range (8):
                    pygame.draw.rect(screen, COLORS[(i+j)%2], (i*C, j*C, C, C))
    
    def show_pieces(self, screen):
        for piece in self.game.pieces:
            piece.show_yourself(screen, self.reverse)
    
    def show_grabbed_piece(self, screen, pos):
        if not self.grabbed_piece.empty:
            screen.blit(self.grabbed_piece.image, pos)
    
    def show_legal_moves(self, screen):
        for coord in self.highlighted_moves:
            i, j = coord
            if self.reverse:
                i, j = 7-i, 7-j
            pygame.draw.rect(screen, HIGHLIGHTED_COLORS[(i+j)%2], (j*C, i*C, C, C))

    def grab_piece(self, i, j):
        if self.reverse:
            i, j = 7-i, 7-j
        square = self.game.board[i][j]
        if not (square.empty or (square.team ^ self.game.turn)):
            self.grabbed_piece = self.game.board[i][j]
            self.highlighted_moves = self.grabbed_piece.legal_moves(self.game)
    
    def drop_piece(self, i, j):
        if self.reverse:
            i, j = 7-i, 7-j
        if (i, j) in self.highlighted_moves:
            self.game.push(self.grabbed_piece.coord, (i, j))
        self.grabbed_piece = Square()
        self.highlighted_moves = []


def main(FEN):
    finished = False
    pygame.init()
    screen = pygame.display.set_mode((C*8, C*8))
    pygame.display.set_caption("Chess")
    clock = pygame.time.Clock()
    chess = Chess(FEN)
    while not finished:
        pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                chess.grab_piece(pos[1]//C, pos[0]//C)
            elif event.type == pygame.MOUSEBUTTONUP:
                chess.drop_piece(pos[1]//C, pos[0]//C)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                chess.rotate_board()
        chess.show_board(screen)
        chess.show_legal_moves(screen)
        chess.show_pieces(screen)
        chess.show_grabbed_piece(screen, (pos[0]-C//2, pos[1]-C//2))     
        clock.tick(FPS)
        pygame.display.update()
    pygame.quit()
    pass

main(FEN)

#print(isattacked(FEN_to_info('rnbqkbnr/ppp2ppp/8/1B1pp3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 1 3')[0], 1, (4, 6)))

#game = Board(FEN_to_info('rnbqkbnr/ppp2ppp/8/1B1pp3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 1 3'))

#print(game.push)
