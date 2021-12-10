from random import choice

def get_best_move(checkers, depth):
    player_num = checkers.player_turn

    root = __Node(None)

    minimax(root, checkers, depth, player_num)

    scores = [node.score for node in root.next_nodes]

    best_moves = []
    for i in range(len(root.next_nodes)):
        if scores[i] == max(scores):
            best_moves.append(root.next_nodes[i].move)
    
    return choice(best_moves)

def minimax(node, checkers, depth, player_num):
    if checkers.end:
        if checkers.winner == -1:
            return 0
        return 1e10*(-1, 1)[checkers.winner == player_num]
    if depth == 0:
        return (checkers.board == (2*player_num + 1)).sum()\
           + 4*(checkers.board == (2*player_num + 2)).sum()\
           -   (checkers.board == (2*(1 - player_num) + 1)).sum()\
           - 4*(checkers.board == (2*(1 - player_num) + 1)).sum()
    
    if checkers.player_turn == player_num:
        # maximizing player
        val = -1e10
        for move in checkers.calc_available_moves_for_player(checkers.player_turn):
            child_checkers = checkers.copy()
            child_checkers.make_move(move, False)
            child_node = __Node(move)
            node.next_nodes.append(child_node)
            val = max(val, minimax(child_node, child_checkers, depth - 1, player_num))

        node.score = val
        return val
    else:
        # minimizing player
        val = 1e10
        for move in checkers.calc_available_moves_for_player(checkers.player_turn):
            child_checkers = checkers.copy()
            child_checkers.make_move(move, False)
            child_node = __Node(move)
            node.next_nodes.append(child_node)
            val = min(val, minimax(child_node, child_checkers, depth - 1, player_num))

        node.score = val
        return val

class __Node(object):
    def __init__(self, move):
        self.move = move
        self.score = 0
        self.next_nodes = []