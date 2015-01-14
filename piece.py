__author__ = 'madanrp'

from reversi.utility import *

class Piece(object):
    "This represents each piece in 8x8 board"

    def __init__(self, x, y):
        self.x = x
        self.y = y
        #self.colour = colour
        self.state = BOARD
        self.flipped = False

    def get_state(self):
        return self.state

    def flip_state(self):
        if self.state == WHITE:
            self.state = BLACK
        elif self.state == BLACK:
            self.state = WHITE
        else:
            raise ValueError

        self.flipped = True

    def set_flipped(self):
        self.flipped = True

    def reset_flipped(self):
        self.flipped = False

    def is_flipped(self):
        return self.flipped

    def get_position(self):
        return (self.x, self.y)

    def set_state(self, state):
        self.state = state

    def get_string(self):
        if self.state == WHITE:
            return "O"
        elif self.state == BLACK:
            return "X"
        else:
            return "*"

    def __str__(self):
        return self.get_string()