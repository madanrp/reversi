__author__ = 'madanrp'
from random import randint
from reversi.competition_utility import *
from reversi.utility import *
positional_weights_competition = []


def CONV_64_91(n):
    return 10+((n)&7)+9*((n)>>3)
def CONV_91_64(n):
    return ((n)%9-1)+(((n)/9-1)<<3)

class EmptyList(object):
    def __init__(self):
        self.prev = None
        self.next = None
        self.square = None

def OTHER(x):
    return 3 - x

emHead = None
emSize = 0
cornerNodes = [None, None, None, None]
nEmptyCorners = 0
#adjCornerNodes = [[None, None],[None, None],[None, None],[None, None],[None, None]]
allNodes = [None for i in range(91)]

class CompetitionPruner(object):
    def __init__(self, depth, first_player, second_player, board):
        self.depth = depth
        # assert isinstance(board, Board)
        self.pieces = board.pieces
        self.infinity = INFINITY
        self.board = 0
        self.move = 1
        self.white = 2
        self.black = 3
        self.first_player = ""
        self.first_player_str = first_player
        self.second_player = ""
        self.second_player_str = second_player
        if first_player == WHITE:
            self.first_player, self.second_player = (self.white, self.black)
        else:
            self.first_player, self.second_player = (self.black, self.white)

        emHead = None
        #self.state = self.make_state(self.pieces)

    def init_discweights(self, base, search_depth):
        currStage = base + search_depth
        # randomnessLevel = 1
        if currStage < STAGE_1_END:
            discWeight = DISC_WEIGHT_STAGE_1

        elif (currStage < STAGE_1_2_START):
            discWeight = DISC_WEIGHT_STAGE_1 + ((DISC_WEIGHT_STAGE_1_2 - DISC_WEIGHT_STAGE_1) *
                                                (currStage - STAGE_1_END)) / (STAGE_1_2_START - STAGE_1_END)

        elif (currStage < STAGE_1_2_END):
            discWeight = DISC_WEIGHT_STAGE_1_2

        elif currStage < STAGE_2_START:
            discWeight = DISC_WEIGHT_STAGE_1 + ((DISC_WEIGHT_STAGE_2 - DISC_WEIGHT_STAGE_1) *
                                                (currStage - STAGE_1_END)) / (STAGE_2_START - STAGE_1_END);
        elif (currStage < STAGE_2_END):
            discWeight = DISC_WEIGHT_STAGE_2
        elif (currStage < STAGE_3_START):
            discWeight = DISC_WEIGHT_STAGE_2 + ((DISC_WEIGHT_STAGE_3 - DISC_WEIGHT_STAGE_2) *
                                                (currStage - STAGE_2_END)) / (STAGE_3_START - STAGE_2_END)

        elif (currStage < STAGE_3_END):
            discWeight = DISC_WEIGHT_STAGE_3
        elif (currStage < STAGE_4_START):
            discWeight = DISC_WEIGHT_STAGE_3 + ((DISC_WEIGHT_STAGE_4 - DISC_WEIGHT_STAGE_3) *
                                                (currStage - STAGE_3_END)) / (STAGE_4_START - STAGE_3_END)
        else:
            discWeight = DISC_WEIGHT_STAGE_4

        #add some randomness
        if (randomnessLevel >= 2):
            randomFactor = (randint(1, 100000) % 4096 / 4096) - 0.5  # +- 0.5
            randomCoeff = 1 + randomnessLevel * randomFactor * RANDOM_FACTOR_CONSTANT
            discWeight *= randomCoeff

        #discWeight = DISC_WEIGHT_TEST;  // debug / test

        discWeightArr = positional_weights_competition
        for i in range(STAGE_1_END):
            discWeightArr[60 - i] = DISC_WEIGHT_STAGE_1
        for i in range(STAGE_1_END, STAGE_1_2_START):
            discWeightArr[60 - i] = DISC_WEIGHT_STAGE_1 + ((DISC_WEIGHT_STAGE_1_2 - DISC_WEIGHT_STAGE_1) *
                                                           (i - STAGE_1_END)) / (STAGE_1_2_START - STAGE_1_END)
        for i in range(STAGE_1_2_START, STAGE_1_2_END):
            discWeightArr[60 - i] = DISC_WEIGHT_STAGE_1_2
        for i in range(STAGE_1_2_END, STAGE_2_START):
            discWeightArr[60 - i] = DISC_WEIGHT_STAGE_1_2 + ((DISC_WEIGHT_STAGE_2 - DISC_WEIGHT_STAGE_1_2) *
                                                             (i - STAGE_1_2_END)) / (STAGE_2_START - STAGE_1_2_END)
        for i in range(STAGE_2_START, STAGE_2_END):
            discWeightArr[60 - i] = DISC_WEIGHT_STAGE_2
        for i in range(STAGE_2_END, STAGE_3_START):
            discWeightArr[60 - i] = DISC_WEIGHT_STAGE_2 + ((DISC_WEIGHT_STAGE_3 - DISC_WEIGHT_STAGE_2) *
                                                           (i - STAGE_2_END)) / (STAGE_3_START - STAGE_2_END)
        for i in range(STAGE_3_START, STAGE_3_END):
            discWeightArr[60 - i] = DISC_WEIGHT_STAGE_3
        for i in range(STAGE_3_END, STAGE_4_START):
            discWeightArr[60 - i] = DISC_WEIGHT_STAGE_3 + ((DISC_WEIGHT_STAGE_4 - DISC_WEIGHT_STAGE_3) *
                                                           (i - STAGE_3_END)) / (STAGE_4_START - STAGE_3_END)
        for i in range(STAGE_4_START, STAGE_4_END):
            discWeightArr[60 - i] = DISC_WEIGHT_STAGE_4
        for i in range(STAGE_4_END, STAGE_5_START):
            discWeightArr[60 - i] = DISC_WEIGHT_STAGE_4 + ((DISC_WEIGHT_STAGE_5 - DISC_WEIGHT_STAGE_4) * (
                i - STAGE_4_END)) / (STAGE_5_START - STAGE_4_END)
        for i in range(STAGE_5_START, 60):
            discWeightArr[60 - i] = DISC_WEIGHT_STAGE_5

        #randomness
        if randomnessLevel >= 2:
            randomFactor = ((float)(randint(1, 100000) % 4096) / 4096) - 0.5  #+- 0.5
            randomCoeff = 1 + randomnessLevel * randomFactor * RANDOM_FACTOR_CONSTANT
            for i in range(1, 61):
                discWeightArr[i] *= randomCoeff


    def copy_board(self, board):
        a = []

        for piece in board.pieces:
            state = piece.get_state()
            if state == WHITE:
                a.append(2)
            elif state == BLACK:
                a.append(1)
            else:
                a.append(0)
        print a
        return a

    def convert_board_91_to_64(self, a):
        to = []
        for i in range(91):
            to.append(i)

        i = 0
        for i in range(len(a)):
            index = CONV_64_91(i)
            to[index] = a[i]

        return to

    def create_empty_list(self,array):
        global emHead
        global emSize
        global allNodes
        global cornerNodes
        global nEmptyCorners
        emHead = EmptyList()
        emSize = 0

        for i in range(4):
            cornerNodes[i] = None

        for i in range(91):
            allNodes[i] = None

        curr_node = emHead
        nEmptyCorners = 0

        i = 63
        while i >= 0:
            place = worst2best[i]
            if array[place] == 0:
                new_node = EmptyList()
                new_node.square = place
                new_node.next = None
                new_node.prev = curr_node
                curr_node = new_node
                emSize += 1
                allNodes[place] = new_node
                if inCorner[place]:
                    cornerNodes[nEmptyCorners] = new_node
                    nEmptyCorners += 1


    def can_flip(self, array, place, direction, color, opp_color):
        result = False
        place_pointer = place + direction
        p = array[place_pointer]
        if p == opp_color:
            count = 0
            while p == opp_color and count < 5:
                place_pointer += direction
                p = array[place_pointer]


        if p == color:
            result = True

        return  result

    def is_move_legal(self, array, color, place):
        p = array[place]
        result = False
        if p == 0:
            return result

        opp_color = OTHER(color)
        dirs = dirmask[place]

        if dirs & 1:
            result = self.can_flip(array, place, directions[0], color, opp_color)
            if result == True:
                return  result

        if dirs & 2:
            result = self.can_flip(array, place, directions[1], color, opp_color)
            if result == True:
                return  result

        if dirs & 4:
            result = self.can_flip(array, place, directions[2], color, opp_color)
            if result == True:
                return  result

        if dirs & 8:
            result = self.can_flip(array, place, directions[3], color, opp_color)
            if result == True:
                return  result

        if dirs & 16:
            result = self.can_flip(array, place, directions[4], color, opp_color)
            if result == True:
                return  result

        if dirs & 32:
            result = self.can_flip(array, place, directions[5], color, opp_color)
            if result == True:
                return  result

        if dirs & 64:
            result = self.can_flip(array, place, directions[6], color, opp_color)
            if result == True:
                return  result

        if dirs & 128:
            result = self.can_flip(array, place, directions[7], color, opp_color)
            if result == True:
                return  result


    def find_legal_moves(self, array, color, legalMoves):
        global  emHead
        count = 0
        curr_node = emHead.next
        while curr_node != None:
            place = curr_node.square
            if self.is_move_legal(array, color, place):
                legalMoves.append(curr_node)
                count += 1
            curr_node = curr_node.next

        return count


    def search_next_move(self, board):
        count_pruning = 0
        count_searching = 0
        count_eval = 0

        base = board.num_actual_moves
        # TODO: add last move if necessary
        depth = 0
        passes = 0
        color = board.player
        curr_value = 0.0
        best_value = -1.0e35
        best_move = "pass"
        alpha = -1.0e35
        beta = 1.0e35

        use_endgame_solver = False
        evaluation_value = 999
        evaluation_value_exact = 999
        WDLresponse = 999


        search_depth = 10
        original_search_depth = search_depth

        bruteForceDepth = 16

        #search_depth = 8
        in_end_game = False
        quiescence_start = 12
        quiescence_search = True

        if (base + 4 + bruteForceDepth) >= 64:
            search_depth = 64
            if 64 - base >= MIN_EMPTIES_FOR_END_GAME_SOLVER:
                use_endgame_solver = True
            in_end_game = True
        else:
            search_depth = original_search_depth
            in_end_game = False
            while search_depth > 4 and base + 4 + search_depth > 64 - MIN_EMPTIES_FOR_MID_GAME_SOLVER:
                search_depth -= 2

        if base + search_depth >= quiescence_start:
            quiescence_search = True
        else:
            quiescence_search = False

        self.init_discweights(base, search_depth)
        #/* extra compensation if search is very shallow */
        DENOMINATOR_EXTRA_DOF = 1
        NEAR_TO_CORNER_NEG_DIAG_COEFF = 0.01
        extra = DENOMINATOR_EXTRA_DOF
        near2cornerDiagCoeff = 1 * NEAR_TO_CORNER_NEG_DIAG_COEFF
        if (search_depth <= 4):
            near2cornerDiagCoeff = 4 * NEAR_TO_CORNER_NEG_DIAG_COEFF
        elif (search_depth <= 6):
            near2cornerDiagCoeff = 2 * NEAR_TO_CORNER_NEG_DIAG_COEFF
        elif (search_depth <= 8):
            near2cornerDiagCoeff = 1 * NEAR_TO_CORNER_NEG_DIAG_COEFF
        elif (search_depth <= 10):
            near2cornerDiagCoeff = 1 * NEAR_TO_CORNER_NEG_DIAG_COEFF
        #// corner weight
        cornerValue = ESTIMATED_CORNER_WORTH




        from_array = self.copy_board(board)
        to_array = self.convert_board_91_to_64(from_array)

        self.create_empty_list(to_array)

        self_pieces = []
        opp_pieces = []

        if self.first_player_str == BLACK:
            self_pieces, opp_pieces = board.count_pieces_player(self.first_player_str, base + depth + 4)
        else:
            opp_pieces, self_pieces = board.count_pieces_player(self.second_player_str, base + depth + 4)

        print self_pieces, opp_pieces

        legal_moves = []
        num_legal_moves = self.find_legal_moves(from_array, color, legal_moves)














