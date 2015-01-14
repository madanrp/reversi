__author__ = 'madanrp'
import datetime
from operator import itemgetter

from reversi.utility import *
from reversi.board import Board



class GenericSearch(object):
    def search_next_move(self):
        pass


positional_weights = [[99, -8, 8, 6, 6, 8, -8, 99],
                      [-8, -24, -4, -3, -3, -4, -24, -8],
                      [8, -4, 7, 4, 4, 7, -4, 8],
                      [6, -3, 4, 0, 0, 4, -3, 6],
                      [6, -3, 4, 0, 0, 4, -3, 6],
                      [8, -4, 7, 4, 4, 7, -4, 8],
                      [-8, -24, -4, -3, -3, -4, -24, -8],
                      [99, -8, 8, 6, 6, 8, -8, 99]]
positional_weights_list = [99, -8, 8, 6, 6, 8, -8, 99,
                           -8, -24, -4, -3, -3, -4, -24, -8,
                           8, -4, 7, 4, 4, 7, -4, 8,
                           6, -3, 4, 0, 0, 4, -3, 6,
                           6, -3, 4, 0, 0, 4, -3, 6,
                           8, -4, 7, 4, 4, 7, -4, 8,
                           -8, -24, -4, -3, -3, -4, -24, -8,
                           99, -8, 8, 6, 6, 8, -8, 99]


infinity = 1.0e400


def state_string(action):
    if len(action) == 4:
        if action == "pass":
            return "pass"
    column = ord('a') + action[0]
    row = ord('0') + action[1] + 1
    return chr(column) + chr(row)


def construct_ab_traverse_log(value, alpha, beta):
    result = []

    for a in [value, alpha, beta]:
        if a == -infinity:
            result.append("-Infinity")
        elif a == infinity:
            result.append("Infinity")
        else:
            result.append(str(value))
    return ",".join(result)


def construct_mm_traverse_log(value):
    result = []
    for a in [value]:
        if a == -infinity:
            result.append("-Infinity")
        elif a == infinity:
            result.append("Infinity")
        else:
            result.append(str(value))
    return ",".join(result)


class AlphaBetaPruner(GenericSearch):
    def __init__(self, depth, first_player, second_player, board):
        self.depth = depth
        # assert isinstance(board, Board)
        self.pieces = board.pieces
        self.infinity = infinity
        self.board = 0
        self.move = 1
        self.white = 2
        self.black = 3
        self.first_player = ""
        self.second_player = ""
        if first_player == WHITE:
            self.first_player, self.second_player = (self.white, self.black)
        else:
            self.first_player, self.second_player = (self.black, self.white)

        self.state = self.make_state(self.pieces)
        self.traverse_log = []


        #print self.state

    def make_state(self, pieces):
        """ Returns a tuple in the form of "current_state", that is: (current_player, state).
        """
        results = {BOARD: self.board, MOVE: self.board, WHITE: self.white, BLACK: self.black}
        return (self.first_player, [results[p.get_state()] for p in pieces])

    def add_traverse_log(self, node, depth, value, alpha, beta):
        self.traverse_log.append("%s,%d,%s" %
                                 (node,
                                  depth,
                                  construct_ab_traverse_log(value, alpha, beta)))

    # @timing
    def search_next_move(self):
        """ Returns a valid action for the AI.
        """
        self.traverse_log = []
        self.traverse_log.append("Node,Depth,Value,Alpha,Beta")
        depth = 0
        alpha = -self.infinity
        beta = self.infinity
        fn = lambda action: self.min_value(depth + 1, self.next_state(self.state, action), alpha,
                                           beta, action)
        maxfn = lambda value: value[0]
        actions = self.actions(self.state)
        actions = sorted(actions, key=lambda x: (x[1], x[0]))
        #print actions
        #moves = [(fn(action), action) for action in actions]
        moves = []
        #print "root", 0, alpha, alpha, beta
        if len(actions) == 0:
            self.add_traverse_log("root", 0, self.evaluation(self.state, self.first_player), alpha, beta)
            return  None, self.traverse_log
        self.add_traverse_log("root", 0, alpha, alpha, beta)
        value = alpha
        #log = "%s,%d,%s"%("root", 0, construct_ab_traverse_log(alpha, alpha, beta))
        for action in actions:
            value = fn(action)
            moves.append((value, action))
            alpha = max(value, alpha)
            #print "root", 0, value, alpha, beta
            self.add_traverse_log("root", 0, value, alpha, beta)
            #self.traverse_log.append("%s,%d,%s"%("root", 0, construct_ab_traverse_log(value, alpha, beta)))

        #print moves
        if len(moves) == 0:
            return None, self.traverse_log

        max_value = max(moves, key=maxfn)[0]

        matching_actions = [move for move in moves if move[0] == max_value]
        #print matching_actions
        matching_actions = sorted(matching_actions, key=lambda x: (x[0], x[1][1], x[1][0]))
        #print matching_actions
        return matching_actions[0][1], self.traverse_log

    def max_value(self, depth, current_state, alpha, beta, action):
        """ Calculates the best possible move for the AI.
        """
        if self.cutoff_test(current_state, depth):
            #print "State=",current_state
            #print "player=", self.second_player
            value = self.evaluation(current_state, self.second_player)
            print state_string(action), depth, value, alpha, beta
            self.add_traverse_log(state_string(action), depth, value, alpha, beta)
            return value
            #pass

        value = -self.infinity
        #print state_string(action), depth, value, alpha, beta
        #self.add_traverse_log(state_string(action), depth, value, alpha, beta)
        actions = self.actions(current_state)
        actions = sorted(actions, key=lambda x: (x[1], x[0]))

        if len(actions) == 0:
            #this is end
            #print "kala"
            #value = self.evaluation(current_state, self.first_player)
            #self.add_traverse_log(state_string(action), depth, value, alpha, beta)
            #return value
            player, state = current_state
            opponent = self.opponent(player)
            tmp_state = state[:]
            opponent_actions = self.get_moves(opponent, player, tmp_state)
            if len(opponent_actions) == 0:
                value = self.evaluation(state, self.first_player)
                self.add_traverse_log(state_string(action), depth, value, alpha, beta)
                return value
            self.add_traverse_log(state_string(action), depth, value, alpha, beta)
            value =  max([value, self.min_value(depth + 1, (opponent, tmp_state), alpha, beta, "pass")])
            if value >= beta:
                alpha = value
                self.add_traverse_log(state_string(action), depth, value, alpha, beta)
                return value
            alpha = max(alpha, value)
            self.add_traverse_log(state_string(action), depth, value, alpha, beta)
            #self.add_traverse_log(state_string(action), depth, value, alpha, beta)
            return value

        self.add_traverse_log(state_string(action), depth, value, alpha, beta)

        for new_action in actions:
            value = max(
                [value, self.min_value(depth + 1, self.next_state(current_state, new_action), alpha, beta, new_action)])
            if value >= beta:
                alpha = value
                #print state_string(action), depth, value, alpha, beta
                self.add_traverse_log(state_string(action), depth, value, alpha, beta)
                return value
            alpha = max([alpha, value])
            #print state_string(action), depth, value, alpha, beta
            self.add_traverse_log(state_string(action), depth, value, alpha, beta)
        return value

    def min_value(self, depth, state, alpha, beta, action):
        """ Calculates the best possible move for the player.
        """
        #print "Inside min_value"
        if self.cutoff_test(state, depth):
            #print "State=",state
            #print self.first_player
            player, curr_state = state
            value = self.evaluation(state, self.first_player)
            print "player=", player
            print state_string(action), depth, value, alpha, beta
            self.add_traverse_log(state_string(action), depth, value, alpha, beta)
            return value
            #pass

        value = self.infinity
        #print state_string(action), depth, value, alpha, beta
        #self.add_traverse_log(state_string(action), depth, value, alpha, beta)
        new_actions = self.actions(state)
        new_actions = sorted(new_actions, key=lambda x: (x[1], x[0]))

        if len(new_actions) == 0:
            #print "mama"
            #this is end
            #value = self.evaluation(state, self.second_player)
            player, curr_state = state
            tmp_state = curr_state[:]
            opponent = self.opponent(player)

            opponent_actions = self.get_moves(opponent, player, tmp_state)
            if len(opponent_actions) == 0:
                value = self.evaluation(state, self.first_player)
                self.add_traverse_log(state_string(action), depth, value, alpha, beta)
                return value
            self.add_traverse_log(state_string(action), depth, value, alpha, beta)
            value =  min([value, self.max_value(depth + 1, (opponent, tmp_state), alpha, beta, "pass")])
            if value <= alpha:
                beta = value
                self.add_traverse_log(state_string(action), depth, value, alpha, beta)
                return value
            beta = min([beta, value])
            self.add_traverse_log(state_string(action), depth, value, alpha, beta)
            #self.add_traverse_log(state_string(action), depth, value, alpha, beta)
            return value
        #print new_actions
        self.add_traverse_log(state_string(action), depth, value, alpha, beta)
        for new_action in new_actions:
            value = min([value, self.max_value(depth + 1, self.next_state(state, new_action), alpha, beta, new_action)])
            if value <= alpha:
                #print "value <= alpha, returning", value
                beta = value
                #print state_string(action), depth, value, alpha, beta
                self.add_traverse_log(state_string(action), depth, value, alpha, beta)
                return value
            beta = min([beta, value])
            #print state_string(action), depth, value, alpha, beta
            self.add_traverse_log(state_string(action), depth, value, alpha, beta)

        #print "returning value", value
        return value

    def actions(self, current_state):
        """ Returns a list of tuples as coordinates for the valid moves for the current player.
        """
        player, state = current_state
        #print state
        #print "Inside actions:", player, state
        return self.get_moves(player, self.opponent(player), state)

    def opponent(self, player):
        """ Returns the opponent of the specified player.
        """
        return self.second_player if player is self.first_player else self.first_player

    def next_state(self, current_state, action):
        """ Returns the next state in the form of a "current_state" tuple, (current_player, state).
        """
        player, state = current_state
        #print action
        tmp_state = state[:]
        opponent = self.opponent(player)

        #print "state move 1=", tmp_state
        xx, yy = action
        tmp_state[xx + (yy * WIDTH)] = player
        for d in DIRECTIONS:
            tile = xx + (yy * WIDTH) + d
            if tile < 0 or tile >= 64:
                continue

            move_in_direction = False
            while tmp_state[tile] != self.board:
                if tmp_state[tile] == player:
                    move_in_direction = True
                    break
                tile += d
                if tile < 0 or tile > WIDTH * HEIGHT:
                    tile -= d
                    break
            tile = xx + (yy * WIDTH) + d
            if move_in_direction:
                while tmp_state[tile] != self.board:
                    tmp_state[tile] = player
                    tile += d
                    if tile < 0 or tile >= WIDTH * HEIGHT:
                        tile -= d
                        break

        #print "state move 2=", tmp_state

        print "opp=",opponent, tmp_state

        return opponent, tmp_state

    def get_moves(self, player, opponent, state):
        """ Returns a generator of (x,y) coordinates.
        """
        #print "opponent=", opponent
        #print "player=", player
        #for tile in range(WIDTH * HEIGHT):
        #    if state[tile] == player:
        #        for d in DIRECTIONS:
        #            print outside_board(tile, d)

        moves = [self.mark_move(player, opponent, tile, state, d)
                 for tile in range(WIDTH * HEIGHT)
                 for d in DIRECTIONS
                 if not outside_board(tile, d) and state[tile] == player]

        #print "Moves = ",moves

        return [(x, y) for found, x, y, tile in moves if found]


    def mark_move(self, player, opponent, tile, pieces, direction):
        """ Returns True whether the current tile piece is a move for the current player,
            otherwise it returns False.
        """
        if not outside_board(tile, direction):
            tile += direction
        else:
            return False, int(tile % WIDTH), int(tile / HEIGHT), tile

        if pieces[tile] == opponent:
            while pieces[tile] == opponent:
                if outside_board(tile, direction):
                    break
                else:
                    tile += direction

            if pieces[tile] == self.board:
                return True, int(tile % WIDTH), int(tile / HEIGHT), tile

        return False, int(tile % WIDTH), int(tile / HEIGHT), tile

    def cutoff_test(self, state, depth):
        """ Returns True when the cutoff limit has been reached.
        """
        #print "inside cutoff_test cut off =", depth >= self.depth
        return depth >= self.depth

    def evaluation(self, current_state, player_to_check):
        """ Returns a positive value when the player wins.
            Returns zero when there is a draw.
            Returns a negative value when the opponent wins."""

        player_state, state = current_state
        player = player_to_check
        opponent = self.opponent(player)
        print "player=%d, opponent=%d"%(player, opponent)
        player_score = 0
        opponent_score = 0
        for index, tile in enumerate(state):
            if tile == player:
                player_score += positional_weights_list[index]
            elif tile == opponent:
                opponent_score += positional_weights_list[index]
        print player_score, opponent_score
        return (player_score - opponent_score)


class MinMax(AlphaBetaPruner):
    def __init__(self, depth, first_player, second_player, board):
        super(MinMax, self).__init__(depth, first_player, second_player, board)

    def add_traverse_log_mm(self, node, depth, value):
        self.traverse_log.append("%s,%d,%s" %
                                 (node,
                                  depth,
                                  construct_mm_traverse_log(value)))

    def search_next_move(self):
        """ Returns a valid action for the AI.
        """
        depth = 0
        self.traverse_log = []
        self.traverse_log.append("Node,Depth,Value")
        fn = lambda action: self.min_value_mm(depth + 1, self.next_state(self.state, action), action)
        maxfn = lambda value: value[0]
        actions = self.actions(self.state)
        actions = sorted(actions, key=lambda x: (x[1], x[0]))

        value = -self.infinity
        # print "root", 0, value
        self.add_traverse_log_mm("root", 0, value)
        #print actions
        #moves = [(fn(action), action) for action in actions]
        moves = []
        for action in actions:
            result = fn(action)
            moves.append((result, action))
            value = max(result, value)
            #print "root ", 0, value
            self.add_traverse_log_mm("root", 0, value)

        #print moves
        if len(moves) == 0:
            #print "No moves"
            return None, self.traverse_log

        max_value = max(moves, key=maxfn)[0]

        matching_actions = [move for move in moves if move[0] == max_value]
        #print matching_actions
        matching_actions = sorted(matching_actions, key=lambda x: (x[0], x[1][1], x[1][0]))
        #print matching_actions
        return matching_actions[0][1], self.traverse_log

    def max_value_mm(self, depth, current_state, action):
        """ Calculates the best possible move for the AI.
        """
        if self.cutoff_test(current_state, depth):
            # print "State=",current_state
            #print "player=", self.second_player
            result = self.evaluation(current_state, self.first_player)
            #m = ord(action[0]) + ord('a')
            #n = ord(action[1]) + ord('0') + 1
            #print state_string(action), depth, result
            self.add_traverse_log_mm(state_string(action), depth, result)
            return result
            #pass

        value = -self.infinity

        # print state_string(action), depth, value
        self.add_traverse_log_mm(state_string(action), depth, value)
        new_actions = self.actions(current_state)
        new_actions = sorted(new_actions, key=lambda x: (x[1], x[0]))
        for new_action in new_actions:
            #print new_action
            #print "before=", current_state
            value = max([value, self.min_value_mm(depth + 1, self.next_state(current_state, new_action), new_action)])
            #print state_string(action), depth, value
            self.add_traverse_log_mm(state_string(action), depth, value)
        #m = ord(action[0]) + ord('a')
        #n = ord(action[1]) + ord('0') + 1

        return value

    def min_value_mm(self, depth, state, action):
        """ Calculates the best possible move for the player.
        """
        # print "Inside min_value"
        if self.cutoff_test(state, depth):
            #print "State=",state
            #print self.first_player
            result = self.evaluation(state, self.second_player)
            #m = ord(action[0]) + ord('a')
            #n = ord(action[1]) + ord('0') + 1
            #print state_string(action), depth, result
            self.add_traverse_log_mm(state_string(action), depth, result)
            return result
            #pass

        value = self.infinity

        #print state_string(action), depth, value
        self.add_traverse_log_mm(state_string(action), depth, value)
        new_actions = self.actions(state)
        new_actions = sorted(new_actions, key=lambda x: (x[1], x[0]))
        #print new_actions
        for new_action in new_actions:
            #print new_action
            #print "before=", state
            value = min([value, self.max_value_mm(depth + 1, self.next_state(state, new_action), new_action)])
            #print state_string(action), depth, value
            self.add_traverse_log_mm(state_string(action), depth, value)
        #print "returning value", value
        #m = ord(action[0]) + ord('a')
        #n = ord(action[1]) + ord('0') + 1

        return value

    def evaluation(self, current_state, player_to_check):
        """ Returns a positive value when the player wins.
            Returns zero when there is a draw.
            Returns a negative value when the opponent wins."""

        player_state, state = current_state
        player = player_to_check
        opponent = self.opponent(player)
        # print "player=%d, opponent=%d"%(player, opponent)
        player_score = 0
        opponent_score = 0
        #print state
        for index, tile in enumerate(state):
            if tile == player:
                player_score += positional_weights_list[index]
            elif tile == opponent:
                opponent_score += positional_weights_list[index]
        #print player_score, opponent_score
        return (player_score - opponent_score)




        



class Player(object):
    def __init__(self, task, depth, color):
        self.task = task
        self.depth = depth
        self.color = color
        self.second_player = BLACK if self.color is WHITE else WHITE

    def next_move(self, first_player, second_player, board):
        if self.task == 3:
            # print "Player: next move"
            alpha_beta_pruner = AlphaBetaPruner(self.depth, self.color, self.second_player, board)
            try:
                return alpha_beta_pruner.search_next_move()
            except Exception, e:
                return None

        elif self.task == 2:
            min_max = MinMax(self.depth, self.color, self.second_player, board)

            try:
                return min_max.search_next_move()
            except Exception, e:
                return None

        elif self.task == 1:
            greedy = MinMax(1, self.color, self.second_player, board)

            try:
                return greedy.search_next_move()
            except Exception, e:
                return None

