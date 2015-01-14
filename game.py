__author__ = 'madanrp'

from reversi.utility import *
from reversi.player import Player
class Game(object):
    def __init__(self, board, depth, player, task):
        self.board = board
        self.max_depth = depth
        self.task = task
        self.second_player = BLACK if player is WHITE else WHITE
        self.first_player = player
        self.player = Player(task, depth, player)


    def next_move(self):
        #print "inside Game:next move"
        traverse_log = ""
        return self.player.next_move(self.first_player, self.second_player, self.board)





