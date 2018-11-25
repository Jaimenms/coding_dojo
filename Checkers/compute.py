from collections import defaultdict
from operator import itemgetter
from random import random

class Spot(object):
    board_len = 8

    def __init__(self, i, j, value):
        self.i = i
        self.j = j
        self.value = value
        self.kind = value.lower()
        self.is_king = self.check_is_king()

    def check_is_king(self):
        if self.kind != "_" and self.kind == self.kind.upper():
            return True
        else:
            return False

    def find_ncap_moves(self, disc_board):
        pass

    def find_cap_moves(self, disc_board):
        pass


class Disc(Spot):
    opps = {'w': ('b', 'B'), 'W': ('b', 'B'), 'b': ('w', 'W'), 'B': ('w', 'W')}
    moves_k = [(-1, -1), (+1, +1), (+1, -1), (-1, +1), ]
    moves_b = [(+1, +1), (+1, -1), ]
    moves_w = [(-1, -1), (-1, +1), ]
    moves = {'w': moves_w, 'b': moves_b, 'W': moves_k, 'B': moves_k}

    def __init__(self, i, j, value):

        Spot.__init__(self, i, j, value)

    def find_ncap_moves(self, disc_board):

        pos_min = 0
        pos_max = 7

        value = self.value

        move_arr = []
        for di, dj in self.moves[value]:

            i2, j2 = self.i + di, self.j + dj

            if i2 < pos_min or j2 < pos_min or i2 > pos_max or j2 > pos_max:
                continue

            value2 = disc_board[i2][j2].value

            if value2 == "_":
                move_arr.append((i2, j2, 0, 0))

        return move_arr

    def find_cap_moves(self, disc_board):

        pos_min = 0
        pos_max = 7

        value = self.value

        move_arr = []

        for di, dj in self.moves[value]:

            eaten = 0
            eatenking = 0

            previous_move = "none"

            for k in range(1, 3):

                i2, j2 = self.i + k * di, self.j + k * dj

                # If out of the board
                if i2 < pos_min or j2 < pos_min or i2 > pos_max or j2 > pos_max:
                    continue

                value2 = disc_board[i2][j2].value

                # If found an equal
                if value2 in (value.lower(), value.upper()):
                    break

                # If found an opponent
                elif value2 in self.opps[value]:
                    # If the previous move was eat
                    if previous_move in ('eat','eatking'):
                        previous_move = "none"
                        break
                    # If the previous move was not eat
                    else:
                        eaten += 1
                        if value2 == value2.upper():
                            eaten += 1
                            previous_move = "eat"
                        else:
                            eatenking += 1
                            previous_move = "eatking"

                # If found empty place
                elif value2 == "_":
                    # If the previous move was eat
                    if previous_move in ('eat','eatking'):
                        previous_move = "none"
                        move_arr.append((i2, j2, eaten,eatenking))
                    # If the previous move was not eat
                    else:
                        break
                else:
                    break

        return move_arr


class Board(object):
    other_player_dict = {'w': 'b', 'b': 'w'}
    board_len = 8
    opps = {'w': ('b', 'B'), 'W': ('b', 'B'), 'b': ('w', 'W'), 'B': ('w', 'W')}

    def __init__(self, board, player, next_disc=None):
        self.left = None
        self.child = []
        self.data = []
        self.board = board
        self.next_disc = next_disc

        self.player = player
        self.other_player = self.other_player_dict[player]

        self.index_player = self.find_disc_index(self.player)
        self.index_other_player = self.find_disc_index(self.other_player)

        self.index_king_player = self.find_king_disc_index(self.player)
        self.index_king_other_player = self.find_king_disc_index(self.other_player)

        self.disc_board = self.find_discs()

        self.analyse_disc_board()

        self.moves_player, self.has_eaten_player, self.has_eatenking_player = self.find_movements(self.index_player, next_disc=next_disc)
        self.moves_other_player, self.has_eaten_other_player, self.has_eatenking_other_player = self.find_movements(self.index_other_player)

        self.who_won = self.check_who_won()
        self.score = (len(self.index_player) + 2*len(self.index_king_player)) / (len(self.index_player) + len(self.index_other_player))
        self.score_other_player = (len(self.index_other_player) + 2*len(self.index_king_other_player)) / (len(self.index_player) + len(self.index_other_player))
        self.king_score = (len(self.index_king_player)) / (len(self.index_player) + len(self.index_other_player))
        self.king_score_other_player = (len(self.index_king_other_player)) / (len(self.index_player) + len(self.index_other_player))
        self.density = self.calculate_density()
        self.main_score = 5*self.king_score+self.score


    def calculate_density(self):

        return (len(self.index_player) + len(self.index_other_player)) / 24

    def calculate_score(self):

        return (len(self.index_player)*len(self.index_king_player)) / (len(self.index_player) + len(self.index_other_player))


    def find_disc_index(self, kind):

        disc_index = []
        for i in range(0, self.board_len):
            for j in range(0, self.board_len):
                value = self.board[i][j]
                if value.lower() == kind:
                    disc_index.append((i, j, kind))

        return disc_index

    def find_king_disc_index(self, kind):

        disc_index = []
        for i in range(0, self.board_len):
            for j in range(0, self.board_len):
                value = self.board[i][j]
                if value == kind.upper():
                    disc_index.append((i, j, kind))

        return disc_index

    def __str__(self):

        for row in self.board:
            print("".join(row))

    def check_who_won(self):
        if len(self.moves_player.keys()) == 0:
            return self.player
        elif len(self.moves_other_player.keys()) == 0:
            return self.other_player
        else:
            return ""

    def find_discs(self):
        disc_board = []
        for i in range(0, self.board_len):
            row = []
            for j in range(0, self.board_len):
                value = self.board[i][j]
                if value == "_":
                    row.append(Spot(i, j, value))
                else:
                    row.append(Disc(i, j, value))
            disc_board.append(row)
        return disc_board

    def analyse_disc_board(self):
        for i in range(0, self.board_len):
            for j in range(0, self.board_len):
                dsc = self.disc_board[i][j]
                if dsc.value != "_":
                    self.disc_board[i][j] = self.analyse_disc(dsc)

    def analyse_disc(self, dsc):

        dsc.ncap_moves = dsc.find_ncap_moves(self.disc_board)
        dsc.cap_moves = dsc.find_cap_moves(self.disc_board)

        return dsc

    def find_movements(self, index, next_disc=None):

        possible_moves = {}
        has_cap = False
        has_eatenking = False

        if not possible_moves:

            for (i, j, _) in index:

                if next_disc is not None:
                    if next_disc[0] != i or next_disc[1] != j:
                        continue

                dsc = self.disc_board[i][j]
                possible_move = dsc.cap_moves
                if possible_move:
                    possible_moves[(i, j)] = possible_move
                    for move in possible_move:
                        if move[3] > 0:
                            has_eatenking = True

                    has_cap = True

        if not possible_moves and next_disc is None:

            for (i, j, _) in index:

                if next_disc is not None:
                    if next_disc[0] != i or next_disc[1] != j:
                        continue

                dsc = self.disc_board[i][j]
                possible_move = dsc.ncap_moves
                if possible_move:
                    possible_moves[(i, j)] = possible_move

        return possible_moves, has_cap, has_eatenking

    def move_board(self, dsc, move):

        from_i, from_j = dsc.i, dsc.j
        to_i, to_j, eaten,_ = move

        board2 = self.board.copy()

        new_king = False
        # Changing destiny
        if not dsc.is_king and dsc.kind == 'w' and to_i == 6:
            value = "W"
            new_king = True
        elif not dsc.is_king and dsc.kind == 'b' and to_i == 0:
            value = "B"
            new_king = True
        else:
            value = dsc.value
        board2[to_i][to_j] = value

        # Changing path
        d = abs(to_i - from_i)
        direction_i = int(abs(to_i - from_i) / (to_i - from_i))
        direction_j = int(abs(to_j - from_j) / (to_j - from_j))
        for di in range(0, d):
            part_i = from_i + di * direction_i
            part_j = from_j + di * direction_j
            board2[part_i][part_j] = "_"

        return board2, new_king


class BoardSequence(Board):

    def __init__(self, board, player):

        Board.__init__(self, board, player)

        key = None

        sequence = []

        initial_position = None

        while True:

            # Read board
            bd = Board(board, player, next_disc=key)

            # Check if possible movies
            possible_moves = bd.moves_player
            if not possible_moves:
                break


            score_list = []
            scores = []
            distances = []
            for key_k in possible_moves.keys():
                dsc_k = bd.disc_board[key_k[0]][key_k[1]]
                for move_k in possible_moves[key_k]:
                    eaten = move_k[2]
                    if eaten == 0:
                        player_k = bd.other_player_dict[player]
                        board_k, new_king_k = self.move_board(dsc_k, move_k)
                        bd_k = Board(board_k, player_k, next_disc=key)
                        score = (len(self.index_other_player) + 5 * len(self.index_king_other_player) - 5*new_king_k - 5*bd_k.has_eatenking_player - 1*bd_k.has_eaten_player)/(len(bd_k.index_player) + len(bd_k.index_other_player))
                    else:
                        player_k = player
                        board_k, new_king_k = self.move_board(dsc_k, move_k)
                        bd_k = Board(board_k, player_k, next_disc=key)
                        score = (len(self.index_player) + 5 * len(self.index_king_player) + 5*new_king_k + 5*bd_k.has_eatenking_player + 1*bd_k.has_eaten_player)/(len(bd_k.index_player) + len(bd_k.index_other_player))

                    distance = self.distance(bd_k)
                    distances.append(distance)
                    score_list.append((key_k, move_k, score, distance))
                    scores.append(score)

            max_score = max(scores)
            min_distance = min(distances)
            if max_score>=0:
                possible_moves2 = defaultdict(list)
                for key_k, move_k, score, distance in score_list:
                    if score == max_score:
                        possible_moves2[key_k].append(move_k)
                bd.moves_player = possible_moves2
            else:
                possible_moves2 = defaultdict(list)
                for key_k, move_k, score, distance in score_list:
                    if distance == min_distance:
                        possible_moves2[key_k].append(move_k)
                bd.moves_player = possible_moves2

            # Strategy 1

            keys = self.prioritize_disc(bd)
            key = keys[0]
            move = bd.moves_player[key][0]


            if initial_position is None:
                initial_position = key
            sequence.append((move[0], move[1],))

            i, j = key

            dsc = bd.disc_board[i][j]

            board2, new_king = self.move_board(dsc, move)

            board = board2
            key = (move[0], move[1])
            eaten = move[2]
            if eaten == 0 or new_king:
                break

        self.initial_position = initial_position
        self.sequence = sequence


    def distance(self, bd):

        d = 0
        for i1,j1,k1 in bd.index_player:
            for i2, j2, ks in bd.index_other_player:
                d += (i2-i1)**2 + (j2-j1)**2

        return d

    def prioritize_disc(self, bd):

        firstrow = {"b": 0, "w": 7, }
        rowsign = {"b": 1, "w": -1, }

        score = []
        for (i, j) in bd.moves_player.keys():
            scorei = 0.01*random()
            if bd.disc_board[i][j].is_king:
                if i == firstrow[bd.player] and bd.score < 0.7:
                    scorei += 10*random()
                scorei += rowsign[bd.player] * i
                if j == 0 or j == 7:
                    scorei += 0.5*random()
                if j == 1 or j == 6:
                    scorei += 0.25*random()
                if j == 2 or j == 5:
                    scorei += 0.1*random()

            score.append(scorei)

        keys = list(bd.moves_player.keys())
        keys = [x for _, x in sorted(zip(score, keys))]

        return keys


#######

def get_next_player():
    return input()


def get_n():
    return int(input())


def get_board(n):
    return [list(input()) for _ in range(n)]


################

next_player = get_next_player()
n = get_n()
board = get_board(n)

bd = BoardSequence(board, next_player)
n = len(bd.sequence)
print(n)
print(" ".join(list(map(str, bd.initial_position))))
for move in bd.sequence:
    print(" ".join(list(map(str, move))))




