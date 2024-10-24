import numpy as np

EMPTY = 0   # Empty Square
BLACK = -1  # Black Disc
WHITE = 1   # White Disc

DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),
              ( 0, -1),          ( 0, 1),
              ( 1, -1), ( 1, 0), ( 1, 1)]

BLACK_PLAYER = -1
WHITE_PLAYER = 1

def get_opponent(My_Player):
    return BLACK_PLAYER if My_Player == WHITE_PLAYER else WHITE_PLAYER
def count_corners(board: np.array, player)->int:
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    corner_count = 0

    for x, y in corners:
        if board[x][y] == player:
            corner_count += 1

    return corner_count

def positional_score(board:np.array, player):
    # Position based Weight
    weights = [
        [ 100, -20, 10,  5,  5, 10, -20, 100],
        [ -20, -50, -2, -2, -2, -2, -50, -20],
        [  10,  -2,  3,  2,  2,  3,  -2,  10],
        [   5,  -2,  2,  1,  1,  2,  -2,   5],
        [   5,  -2,  2,  1,  1,  2,  -2,   5],
        [  10,  -2,  3,  2,  2,  3,  -2,  10],
        [ -20, -50, -2, -2, -2, -2, -50, -20],
        [ 100, -20, 10,  5,  5, 10, -20, 100]
    ]

    score = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == player:
                score += weights[x][y]               # Score of My Disc
            elif board[x][y] == get_opponent(player):
                score -= weights[x][y]               # Score of Opponent's Disc

    return score

def count_discs(board, player):
    return sum(row.count(player) for row in board)

def get_valid_moves(board, player):
    opponent = get_opponent(player)
    valid_moves = []

    for x in range(8):
        for y in range(8):
            if board[x][y] != EMPTY:
                continue

            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                has_opponent_between = False

                while 0 <= nx < 8 and 0 <= ny < 8 and board[nx][ny] == opponent:
                    nx += dx
                    ny += dy
                    has_opponent_between = True

                if has_opponent_between and 0 <= nx < 8 and 0 <= ny < 8 and board[nx][ny] == player:
                    valid_moves.append((x, y))
                    break

    return valid_moves

def get_game_phase(board):
    empty_count = sum(row.count(EMPTY) for row in board)
    total_squares = 64

    if empty_count > 44:
        return 'opening'  # Num of Empty > 44
    elif empty_count > 20:
        return 'midgame'  # Num of Empty > 20
    else:
        return 'endgame'  # Else

def calculate_stability(board):
    stable = [[False for _ in range(8)] for _ in range(8)]
    directions = DIRECTIONS

    # Find the stable disc
    corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
    for x, y in corners:
        if board[x][y] != EMPTY:
            mark_stable_from_corner(board, stable, x, y)

    return stable

def mark_stable_from_corner(board, stable, x, y):
    player = board[x][y]
    queue = [(x, y)]
    stable[x][y] = True

    while queue:
        cx, cy = queue.pop(0)
        for dx, dy in DIRECTIONS:
            nx, ny = cx + dx, cy + dy
            while 0 <= nx < 8 and 0 <= ny < 8:
                if board[nx][ny] != player or stable[nx][ny]:
                    break
                stable[nx][ny] = True
                queue.append((nx, ny))
                nx += dx
                ny += dy


def positional_score_Stable(board, player, stable):
    # Position based Weight
    weights = [
        [ 200, 100, 100, 100, 100, 100, 100, 200],
        [ 100,  10,  10,  10,  10,  10,  10, 100],
        [ 100,  10,  10,  10,  10,  10,  10, 100],
        [ 100,  10,  10,  10,  10,  10,  10, 100],
        [ 100,  10,  10,  10,  10,  10,  10, 100],
        [ 100,  10,  10,  10,  10,  10,  10, 100],
        [ 100,  10,  10,  10,  10,  10,  10, 100],
        [ 200, 100, 100, 100, 100, 100, 100, 200]
    ]


    score = 0
    for x in range(8):
        for y in range(8):
            if not stable[x][y]:
                continue  # Only consider the stable Disc
            if board[x][y] == player:
                score += weights[x][y]
            elif board[x][y] == get_opponent(player):
                score -= weights[x][y]

    return score

def positional_score_Unstable(board, player, stable):
    # Position based Weight
    weights = [
        [100, -20, 10, 5, 5, 10, -20, 100],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [10, -2, 3, 2, 2, 3, -2, 10],
        [5, -2, 2, 1, 1, 2, -2, 5],
        [5, -2, 2, 1, 1, 2, -2, 5],
        [10, -2, 3, 2, 2, 3, -2, 10],
        [-20, -50, -2, -2, -2, -2, -50, -20],
        [100, -20, 10, 5, 5, 10, -20, 100]
    ]


    score = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == player and not stable[x][y]:
                score += weights[x][y]
            elif board[x][y] == get_opponent(player) and not stable[x][y]:
                score -= weights[x][y]

    return score

###=======================================================================###
###        Evaluation Cost Init: Basic and Typical Approach
###=======================================================================###
def Evaluate_Cost(board, turn):
    My_Player = BLACK_PLAYER if turn == -1 else WHITE_PLAYER
    OP_Player = WHITE_PLAYER if turn ==  1 else BLACK_PLAYER

    # Check the Num of Disc Diff
    my_discs  = count_discs(board, My_Player)
    opp_discs = count_discs(board, OP_Player)
    disc_diff = my_discs - opp_discs

    # Mobility Score
    my_moves  = len(get_valid_moves(board, My_Player))
    opp_moves = len(get_valid_moves(board, OP_Player))
    mobility = my_moves - opp_moves

    # Corner Position Score
    my_corners = count_corners(board, My_Player)
    opp_corners = count_corners(board,OP_Player)
    corner_occupancy = my_corners - opp_corners

    # Position based Score
    position_score = positional_score(board, My_Player)

    # Weight => Could be updated by
    weight_disc_diff = 10   # Range of diff: -64 ~ 64
    weight_mobility = 78    # Range of Mobility: -30 ~ 30
    weight_corner = 800     # Range of Corner: -4 ~ 4
    weight_position = 100   # Range of Weight Position -1200 ~ 1200

    # Total Cost
    score = (
        weight_disc_diff * disc_diff +
        weight_mobility * mobility +
        weight_corner * corner_occupancy +
        weight_position * position_score
    )

    return score

###=======================================================================###
###        Evaluation Cost Rev1: Adding Game Phase and Stability
###=======================================================================###
def Evaluate_Cost_r1(board, turn):
    My_Player = BLACK_PLAYER if turn == -1 else WHITE_PLAYER
    OP_Player = WHITE_PLAYER if turn == 1 else BLACK_PLAYER

    # Check Game Phase
    Game_Phase = get_game_phase(board)

    # Stability: cannot be flipped by the opponent
    stable = calculate_stability(board)

    # The Num of diff of Disc
    my_discs = count_discs(board, My_Player)
    opp_discs = count_discs(board, OP_Player)
    disc_diff = my_discs - opp_discs  # Value Range: -64 ~ +64

    # Mobility Socre
    my_moves = len(get_valid_moves(board, My_Player))
    opp_moves = len(get_valid_moves(board, OP_Player))
    mobility = my_moves - opp_moves  # Value Range: 대략 -30 ~ +30

    # Corner Score
    my_corners = count_corners(board, My_Player)
    opp_corners = count_corners(board, OP_Player)
    corner_occupancy = my_corners - opp_corners  # Value Range: -4 ~ +4

    # Calc Position based Weighted Score with Stable Disc Map
    #position_score = positional_score(board, My_Player)  # Value Range: -1200 ~ +1200
    position_score = positional_score_Unstable(board, My_Player, stable)  # Value Range: -1200 ~ +1200

    # Calc Stability Score
    stable_score = positional_score_Stable(board, My_Player, stable)

    # Weight Change by the num of empty Disc
    if Game_Phase == 'opening':
        weight_disc_diff = 10
        weight_mobility  = 500
        weight_corner    = 801
        weight_position  = 382
        weight_stable    = 100
    elif Game_Phase == 'midgame':
        weight_disc_diff = 10
        weight_mobility  = 78
        weight_corner    = 801
        weight_position  = 682
        weight_stable    = 100
    else:  # 'endgame'
        weight_disc_diff = 800
        weight_mobility  = 10
        weight_corner    = 1000
        weight_position  = 10
        weight_stable    = 100

    # Total Score
    score = (
        weight_disc_diff * disc_diff +
        weight_mobility  * mobility +
        weight_corner    * corner_occupancy +
        weight_position  * position_score +
        weight_stable    * stable_score
    )

    return score

