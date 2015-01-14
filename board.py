__author__ = 'madanrp'

from reversi.piece import Piece
from reversi.utility import *

class Board:
    def __init__(self):
        self.width = 8
        self.height = 8
        self.pieces = list(Piece(x,y)
                            for y in range(0, self.height)
                            for x in range(0, self.width))
        self.num_actual_moves = 0
        self.num_moves_pass = 0
        self.player = BLACK
        self.mirrored = False
        self.moves = []


    def set_state(self, x, y, state):
        """ Sets the specified piece's state.
        """
        self.pieces[x + (y * self.width)].set_state(state)

    #def set_state(self, index, state):
    #    """ Sets the specified piece's (as index) state to WHITE.
    #    """
    #    self.pieces[index].set_state(state)

    #def flip(self, x, y):
    #    """ Flips the specified piece's state from WHITE<->BLACK.
    #    """
    #    #self.pieces[x + (y * self.width)].flip()

    def set_flipped(self, x, y):
        """ Sets the specified piece as flipped.
        """
        self.pieces[x + (y * self.width)].set_flipped()

    def get_move_pieces(self, player):
        """ Returns a list of moves for the specified player.
        """
        self.mark_moves(player)
        moves = [piece for piece in self.pieces if piece.get_state() == MOVE]
        self.clear_moves()
        return moves

    def mark_moves(self, player):
        """ Marks all 'BOARD' pieces that are valid moves as 'MOVE' pieces
            for the current player.

            Returns: void
        """
        [self.mark_move(player, p, d)
         for p in self.pieces
         for d in DIRECTIONS
         if p.get_state() == player]

    def mark_move(self, player, piece, direction):
        """ Will mark moves from the current 'piece' in 'direction'.
        """
        x, y = piece.get_position()
        opponent = get_opponent(player)
        if outside_board(x + (y * WIDTH), direction):
            return

        tile = (x + (y * WIDTH)) + direction

        if self.pieces[tile].get_state() == opponent:
            while self.pieces[tile].get_state() == opponent:
                if outside_board(tile, direction):
                    break
                else:
                    tile += direction

            if self.pieces[tile].get_state() == BOARD:
                self.pieces[tile].set_state(MOVE)

    def make_move(self, coordinates, player):
        """ Will modify the internal state to represent performing the
            specified move for the specified player.
        """
        x, y = coordinates
        print x, y

        moves = [piece.get_position() for piece in self.get_move_pieces(player)]

        if coordinates not in moves:
            raise ValueError

        if (x < 0 or x >= WIDTH) or (y < 0 or y >= HEIGHT):
            raise ValueError

        opponent = get_opponent(player)
        p = self.pieces[x + (y * WIDTH)]
        if player == WHITE:
            p.set_state(WHITE)
        else:
            p.set_state(BLACK)
        for d in DIRECTIONS:
            start = x + (y * WIDTH) + d
            tile = start

            to_flip = []
            if (tile >= 0) and (tile < WIDTH*HEIGHT):
                while self.pieces[tile].get_state() != BOARD:
                    to_flip.append(self.pieces[tile])
                    if outside_board(tile, d):
                        break
                    else:
                        tile += d

                start_flipping = False
                for pp in reversed(to_flip):
                    if not start_flipping:
                        if pp.get_state() == opponent:
                            continue
                    start_flipping = True

                    if player == WHITE:
                        pp.set_state(WHITE)
                    else:
                        pp.set_state(BLACK)

                self.pieces[start].reset_flipped()

    def clear_moves(self):
        """ Sets all move pieces to board pieces.
        """
        [x.set_state(BOARD) for x in self.pieces if x.get_state() == MOVE]

    def draw(self):
        str = self.get_string()
        print str

    def get_string(self):
        str = ""
        for j in range(HEIGHT):
            for i in range(WIDTH):
                index = i + j * WIDTH
                str += self.pieces[index].get_string()
            str += "\n"
        return str

    def count_pieces(self):
        count = 0
        for piece in self.pieces:
            if piece.get_state() != BOARD:
                count += 1
        return count

    def count_pieces_player(self, player, total):
        count = 0
        for piece in self.pieces:
            if piece.get_state() != BOARD:
                count += 1
                if piece.get_state() == WHITE:
                    count += 1
        return 2*total - count, count - total
        #return  count

    def count_and_set(self):
        self.num_actual_moves = self.count_pieces()

    def opponent_last_move(self, opponent):
        for piece in self.pieces:
            position = piece.get_position()
            state = piece.get_state()
            if state == opponent and position not in self.moves:
                print position
                self.moves.append(position)







