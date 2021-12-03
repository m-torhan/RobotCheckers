import numpy as np

class Checkers(object):
    def __init__(self, board=None, turn=None):
        self.__end = False
        self.__player_turn = 0
        self.__board = np.zeros((8, 8), dtype=np.uint8)
        self.__winner = None
        self.__all_moves = []
        self.__turn_counter = 0
        self.__no_taking_queen_moves = [0, 0]

        if board is not None:
            self.__board = board.copy()
        else:
            for i in range(8):
                for j in range(8):
                    if (i + j) % 2 == 1:
                        if j <= 2:
                            self.__board[i, j] = 1
                        elif j >= 5:
                            self.__board[i, j] = 3
        
        if turn is not None:
            self.__player_turn = turn

    @property
    def player_turn(self):
        return self.__player_turn

    @property
    def board(self):
        return self.__board.copy()

    @property
    def end(self):
        return self.__end

    @property
    def winner(self):
        return self.__winner
    
    @property
    def all_moves(self):
        return self.__all_moves

    @property
    def turn_counter(self):
        return self.__turn_counter
    
    def copy(self):
        checkers_copy = Checkers(self.__board.copy())
        checkers_copy.__player_turn = self.__player_turn

        return checkers_copy

    def make_move(self, move, validate=True):
        if validate:
            if not self.is_move_valid(move):
                return False

        if len(move.taken_figures) == 0:
            if self.__figure_type(self.__board[move.src]) == 1:
                self.__no_taking_queen_moves[self.__player_turn] += 1
        else:
            self.__no_taking_queen_moves[self.__player_turn] = 0

        self.__board[move.dest] = self.__board[move.src]
        self.__board[move.src] = 0

        promoted = False
        if self.__figure_type(self.__board[move.dest]) == 0 and\
           ((move.dest[1] == 0 and self.__player_turn == 1) or\
            (move.dest[1] == 7 and self.__player_turn == 0)):
            self.__board[move.dest] = self.__promote_pawn_to_queen(self.__board[move.dest])
            promoted = True

        for taken in move.taken_figures:
            self.__board[taken] = 0
        
        self.__next_player()

        if len(self.calc_available_moves_for_player(self.__player_turn)) == 0:
            self.__end = True
            self.__winner = self.opponent()

        if min(self.__no_taking_queen_moves) > 15:
            self.__end = True
            self.__winner = -1
        
        move.promoted = promoted
        self.__all_moves.append(move)
        
        return True, promoted

    def is_move_valid(self, move):
        # validate steps
        step_src = move.src

        step_board = self.__board.copy()
        for pos in move.chain[1:]:
            step_dest = pos
            if not self.__is_step_valid(step_board, step_src, step_dest):
                return False
            
            step_board = self.__apply_step_to_board(step_board, step_src, step_dest)
            
            step_src = step_dest
        
        # validate taken pawns
        step_src = move.src

        taken_figures = []
        
        step_board = self.__board.copy()
        for pos in move.chain[1:]:
            step_dest = pos
            step_taken = self.__step_taken_figures(step_board, step_src, step_dest)
            if step_taken is not None:
                taken_figures.extend(step_taken)
            
            step_board = self.__apply_step_to_board(step_board, step_src, step_dest)

            step_src = step_dest

        # check if regular move was made while there was
        # available move with opponent figures taking
        if len(taken_figures) == 0:
            for move in self.calc_available_moves_for_player(self.__player_turn):
                if len(move.taken_figures) > 0:
                    return False
        
        if set(taken_figures) != set(move.taken_figures):
            return False
        
        return True

    def calc_available_moves_for_player(self, player):
        pawns = (1 + 2*player, 2 + 2*player)

        moves = []
        
        for i in range(self.board.shape[0]):
            for j in range(self.board.shape[1]):
                if self.__board[i, j] in pawns:
                    moves.extend(self.__calc_available_moves((i, j)))

        has_taking_move = False
        for move in moves:
            if len(move.taken_figures) > 0:
                has_taking_move = True
                break

        if has_taking_move:
            for i in range(len(moves))[::-1]:
                if len(moves[i].taken_figures) == 0:
                    del moves[i]

        return moves

    def calc_move_between_boards(self, new_board):
        curr_board_player_figures = self.__figure_player(self.__board) == self.__player_turn
        new_board_player_figures = self.__figure_player(new_board) == self.__player_turn
        curr_board_opponent_figures = self.__figure_player(self.__board) == self.opponent()
        new_board_opponent_figures = self.__figure_player(new_board) == self.opponent()

        moved_figures_src = (curr_board_player_figures == True) & (new_board_player_figures == False)

        if np.sum(moved_figures_src) != 1:
            return None

        moved_figures_dest = (curr_board_player_figures == False) & (new_board_player_figures == True)

        if np.sum(moved_figures_dest) != 1:
            return None

        moved_figure_src = np.where(moved_figures_src)
        moved_figure_src = (moved_figure_src[0][0], moved_figure_src[1][0])

        moved_figure_dest = np.where(moved_figures_dest)
        moved_figure_dest = (moved_figure_dest[0][0], moved_figure_dest[1][0])

        available_moves = self.__calc_available_moves(moved_figure_src)
        available_moves = list(filter(lambda move: move.dest == moved_figure_dest, available_moves))

        taken_figures = (curr_board_opponent_figures == True) & (new_board_opponent_figures == False)
        placed_opponent_figures = (curr_board_opponent_figures == False) & (new_board_opponent_figures == True)

        if np.sum(placed_opponent_figures) > 0:
            return None

        taken_figures = list(zip(*list(map(list, np.where(taken_figures)))))

        for move in available_moves:
            if set(taken_figures) == set(move.taken_figures):
                if self.__figure_type(self.__board[move.src]) == 0 and\
                   self.__figure_type(new_board[move.dest]) == 1:
                    move.promoted = True
                return move

        return None

    def opponent(self, player=None):
        if player is None:
            return 1 - self.__player_turn
        return 1 - player

    def __is_step_valid(self, step_board, step_src, step_dest):
        # move from empty square
        if step_board[step_src] == 0:
            return False

        # moving not current turn players figure
        if self.__figure_player(step_board[step_src]) != self.__player_turn:
            return False

        # there is figure on dest square
        if step_board[step_dest] != 0:
            return False

        # pawn
        if self.__figure_type(step_board[step_src]) == 0:
            if abs(step_dest[0] - step_src[0]) == 1 and abs(step_dest[1] - step_src[1]) == 1:
                # regular move
                return True

            y_dir = (1, -1)[self.__player_turn]
            if abs(step_dest[0] - step_src[0]) == 2 and step_dest[1] - step_src[1] == 2*y_dir and\
               self.__figure_player(step_board[(step_src[0] + step_dest[0])//2, (step_src[1] + step_dest[1])//2]) == self.opponent():
                # taking move
                return True

        #queen
        if self.__figure_type(step_board[step_src]) == 1:
            if abs(step_dest[0] - step_src[0]) == abs(step_dest[1] - step_src[1]):
                return True

        return False

    def __step_taken_figures(self, step_board, step_src, step_dest):
        # pawn
        if self.__figure_type(step_board[step_src]) == 0:
            if abs(step_src[0] - step_dest[0]) == 2 and abs(step_src[1] - step_dest[1]) == 2 and\
               self.__figure_player(step_board[(step_src[0] + step_dest[0])//2, (step_src[1] + step_dest[1])//2]) == self.opponent():
                # taking move
                return [((step_src[0] + step_dest[0])//2, (step_src[1] + step_dest[1])//2)]

        #queen
        if self.__figure_type(step_board[step_src]) == 1:
            if abs(step_src[0] - step_dest[0]) == abs(step_src[1] - step_dest[1]):
                fields_between = abs(step_src[0] - step_dest[0]) - 1
                x_dir = (-1, 1)[step_dest[0] > step_src[0]]
                y_dir = (-1, 1)[step_dest[1] > step_src[1]]

                pawns = []
                for i in range(fields_between):
                    pos = (step_src[0] + (i + 1)*x_dir,
                           step_src[1] + (i + 1)*y_dir)
                    if self.__figure_player(step_board[pos]) == self.opponent():
                        pawns.append(pos)

                return pawns

        return None

    def __next_player(self):
        self.__player_turn = self.opponent()
        self.__turn_counter += 1

    def __calc_available_moves(self, figure_pos):
        figure_type = self.__figure_type(self.__board[figure_pos])

        if figure_type == 0:
            return self.__calc_available_moves_pawn(figure_pos)
        elif figure_type == 1:
            return self.__calc_available_moves_queen(figure_pos)

    def __calc_available_moves_pawn(self, figure_pos):
        player = self.__figure_player(self.__board[figure_pos])

        x, y = figure_pos

        y_dir = (1, -1)[player]

        available_moves = []

        # taking moves
        def dfs(board, chain, taken_figures):
            pos = chain[-1]
            x, y = pos

            next_taking_possible = False
            for new_pos, taking_pos in (((x - 2, y + 2*y_dir), (x - 1, y + y_dir)),
                                        ((x + 2, y + 2*y_dir), (x + 1, y + y_dir))):
                if 0 <= new_pos[0] <= 7 and\
                   0 <= new_pos[1] <= 7 and\
                   self.__board[new_pos] == 0 and\
                   self.__figure_player(self.__board[taking_pos]) == self.opponent(player):
                    next_taking_possible = True

                    new_board = board.copy()
                    new_board[new_pos] = new_board[pos]
                    new_board[pos] = 0
                    new_board[taking_pos] = 0

                    new_chain = chain.copy()
                    new_chain.append(new_pos)

                    new_taken_figures = taken_figures.copy()
                    new_taken_figures.append(taking_pos)

                    dfs(new_board, new_chain, new_taken_figures)

            if not next_taking_possible and len(chain) > 1:
                available_moves.append(Move(chain, taken_figures))

        dfs(self.__board, [figure_pos], [])

        # regular moves
        if len(available_moves) == 0:
            for new_pos in ((x - 1, y + y_dir),
                            (x + 1, y + y_dir)):
                if 0 <= new_pos[0] <= 7 and\
                0 <= new_pos[1] <= 7 and\
                self.__board[new_pos] == 0:
                    available_moves.append(Move((figure_pos, new_pos), []))

        return available_moves

    def __calc_available_moves_queen(self, figure_pos):
        player = self.__player_turn

        x, y = figure_pos

        available_moves = []

        # taking moves
        def dfs(board, chain, taken_figures):
            pos = chain[-1]
            x, y = pos

            next_taking_possible = False
            for y_dir in [-1, 1]:
                for x_dir in [-1, 1]:
                    new_x = x + x_dir
                    new_y = y + y_dir

                    while 0 <= new_x <= 7 and\
                          0 <= new_y <= 7 and\
                          board[(new_x, new_y)] == 0:
                        new_x += x_dir
                        new_y += y_dir

                    if 0 <= new_x <= 7 and\
                       0 <= new_y <= 7 and\
                       self.__figure_player(board[(new_x, new_y)]) == self.opponent(player):
                        taking_pos = (new_x, new_y)
                        new_x += x_dir
                        new_y += y_dir
                        while 0 <= new_x <= 7 and\
                              0 <= new_y <= 7 and\
                              board[(new_x, new_y)] == 0:
                            next_taking_possible = True

                            new_board = board.copy()
                            new_board[(new_x, new_y)] = new_board[pos]
                            new_board[pos] = 0
                            new_board[taking_pos] = 0

                            new_chain = chain.copy()
                            new_chain.append((new_x, new_y))

                            new_taken_figures = taken_figures.copy()
                            new_taken_figures.append(taking_pos)

                            dfs(new_board, new_chain, new_taken_figures)

                            new_x = new_x + x_dir
                            new_y = new_y + y_dir

            if not next_taking_possible and len(chain) > 1:
                available_moves.append(Move(chain, taken_figures))

        dfs(self.__board, [figure_pos], [])

        # regular moves
        if len(available_moves) == 0:
            for y_dir in [-1, 1]:
                for x_dir in [-1, 1]:
                    new_x = x + x_dir
                    new_y = y + y_dir
                    while 0 <= new_x <= 7 and\
                          0 <= new_y <= 7 and\
                          self.__board[(new_x, new_y)] == 0:
                        available_moves.append(Move((figure_pos, (new_x, new_y)), []))
                        new_x += x_dir
                        new_y += y_dir

        return available_moves

    @staticmethod
    def __apply_step_to_board(board, step_src, step_dest):
        board[step_dest] = board[step_src]
        board[step_src] = 0

        if abs(step_dest[0] - step_src[0]) > 1:
            x_dir = (-1, 1)[step_dest[0] > step_src[0]]
            y_dir = (-1, 1)[step_dest[1] > step_src[1]]
            for i in range(1, abs(step_dest[0] - step_src[0])):
                x = step_src[0] + i*x_dir
                y = step_src[1] + i*y_dir
                board[x, y] = 0

        return board

    @staticmethod
    def __figure_player(pawn):
        return (pawn - 1)//2

    @staticmethod
    def __figure_type(pawn):
        if pawn == 0:
            return -1
        return (pawn - 1)%2

    @staticmethod
    def __promote_pawn_to_queen(pawn):
        if pawn == 0:
            return pawn
        return pawn + 1

class Move(object):
    def __init__(self, chain, taken_figures):
        self.__chain = chain
        self.__taken_figures = taken_figures
        self.__promoted = False

    @property
    def src(self):
        return self.__chain[0]

    @property
    def dest(self):
        return self.__chain[-1]

    @property
    def chain(self):
        return self.__chain

    @property
    def taken_figures(self):
        return self.__taken_figures

    @property
    def promoted(self):
        return self.__promoted

    @promoted.setter
    def promoted(self, value):
        self.__promoted = value

    def __repr__(self):
        return f'Move(chain={self.__chain}, taken={self.__taken_figures}, promoted={self.__promoted})'

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, Move):
            return None
        if self.__chain == other.chain and\
           self.__taken_figures == other.taken_figures and\
           self.__promoted == other.promoted:
            return True
        return False
