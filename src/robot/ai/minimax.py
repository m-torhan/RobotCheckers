from random import choice

def get_best_move(checkers, depth):
    player_num = checkers.player_turn
    root = MoveTreeNode(checkers, player_num, None, 0, 0)

    nodes = [[root]]
    for _ in range(depth):
        nodes.append([])
        for node in nodes[-2]:
            node.add_next_nodes()
            nodes[-1].extend(node.next_nodes)
    
    for layer in nodes[::-1]:
        for node in layer:
            node.calculate_backtrack_score()

    best_score = -1e10
    for node in root.next_nodes:
        if node.backtrack_score > best_score:
            best_score = node.backtrack_score
    
    best_moves = []
    for node in root.next_nodes:
        if node.backtrack_score == best_score:
            best_moves.append(node.move)
    
    return choice(best_moves)

class MoveTreeNode(object):
    def __init__(self, node_checkers, player_num, node_move, score, node_depth):
        self.__node_checkers = node_checkers
        self.__player_num = player_num
        self.__node_move = node_move
        self.__node_score = score
        self.__node_depth = node_depth
        self.__next_nodes = []
        self.__backtrack_score = 0
    
    @property
    def next_nodes(self):
        return self.__next_nodes
        
    @property
    def move(self):
        return self.__node_move
        
    @property
    def score(self):
        return self.__node_score
        
    @property
    def backtrack_score(self):
        return self.__backtrack_score
    
    def add_next_nodes(self):
        available_moves = self.__node_checkers.calc_available_moves_for_player(self.__node_checkers.player_turn)

        for move in available_moves:
            checkers = self.__node_checkers.copy()
            score = 0
            for taken in move.taken_figures:
                # 1 point for pawn, 5 points for queen
                score += ((checkers.board[taken] - 1) % 2)*4 + 1 

            multiplier = (-1, 1)[checkers.player_turn == self.__player_num]

            ret, promoted = checkers.make_move(move)

            if promoted:
                score += 4
            
            score *= multiplier
            
            if ret:
                self.__next_nodes.append(MoveTreeNode(checkers, self.__player_num, move, score, self.__node_depth + 1))
            else:
                print('ERROR')
                print(checkers.board)
                print(move.chain, move.taken_figures)

    def calculate_backtrack_score(self):
        if len(self.__next_nodes) == 0:
            if self.__node_checkers.end:
                if self.__node_checkers.winner != 0:
                    self.__backtrack_score = 1000*(-1, 1)[self.__node_checkers.winner == self.__player_num]
                return

            self.__backtrack_score = self.__node_score
            return
        
        scores = []
        for node in self.__next_nodes:
            scores.append(node.backtrack_score)

        if self.__node_checkers.player_turn == self.__player_num:
            self.__backtrack_score = max(scores) + self.__node_score
        else:
            self.__backtrack_score = min(scores) + self.__node_score