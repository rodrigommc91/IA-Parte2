import math
import random

from Player import Player


class MCTSAIPlayer(Player):
    """
    Agente de IA que utiliza o algoritmo Monte Carlo Tree Search (MCTS)
    implementado de raiz para jogar Connect N.
    """
    
    def __init__(self, piece, max_iterations=1000):
        
        super().__init__(piece)
        self.max_iterations = max_iterations
        self.opponent_piece = 2 if piece == 1 else 1

    def get_move(self, board):
        
        valid_moves = board.get_valid_moves()
        
        if len(valid_moves) == 1:
            return valid_moves[0]
        if not valid_moves:
            return 0

        root = MCTSNode(board.copy(), player_piece=self.piece, opponent_piece=self.opponent_piece)

        for _ in range(self.max_iterations):
            node = root
            
            while node.is_fully_expanded() and not node.is_terminal():
                node = node.best_child_ucb()

            if not node.is_terminal():
                node = node.expand()

            winner = node.simulate()

            node.backpropagate(winner)

        best_child = max(root.children.values(), key=lambda c: c.visits)
        return best_child.move_that_led_here


class MCTSNode:
    def __init__(self, board, parent=None, move_that_led_here=None, player_piece=1, opponent_piece=2):
        self.board = board 
        self.parent = parent 
        self.move_that_led_here = move_that_led_here
        
        self.player_piece = player_piece
        self.opponent_piece = opponent_piece
        
        self.children = {}
        
        self.untried_moves = board.get_valid_moves()
        
        self.visits = 0
        self.wins = 0

    def is_terminal(self):
        return (self.board.check_winner(self.player_piece) or 
                self.board.check_winner(self.opponent_piece) or 
                self.board.is_board_full())

    def is_fully_expanded(self):
        return len(self.untried_moves) == 0

    def expand(self):
        move = self.untried_moves.pop()
        next_board = self.board.copy()
        
        current_turn_piece = self.player_piece if (self.parent_is_opponent_turn()) else self.opponent_piece
        next_board.drop_piece(move, current_turn_piece)
        
        child_node = MCTSNode(
            board=next_board, 
            parent=self, 
            move_that_led_here=move,
            player_piece=self.player_piece,
            opponent_piece=self.opponent_piece
        )
        self.children[move] = child_node
        return child_node

    def parent_is_opponent_turn(self):
        depth = 0
        p = self
        while p.parent is not None:
            depth += 1
            p = p.parent
        return depth % 2 == 0

    def best_child_ucb(self, exploration_constant=1.414):
        best_score = -math.inf
        best_children = []
        
        for child in self.children.values():
            exploitation = child.wins / child.visits
            exploration = exploration_constant * math.sqrt(math.log(self.visits) / child.visits)
            ucb_score = exploitation + exploration
            
            if ucb_score > best_score:
                best_score = ucb_score
                best_children = [child]
            elif ucb_score == best_score:
                best_children.append(child)
                
        return random.choice(best_children)

    def simulate(self):
        temp_board = self.board.copy()
        
        current_piece = self.opponent_piece if self.parent_is_opponent_turn() else self.player_piece
        
        while True:
            if temp_board.check_winner(self.player_piece):
                return self.player_piece
            if temp_board.check_winner(self.opponent_piece):
                return self.opponent_piece
            if temp_board.is_board_full():
                return 0  # Empate
                
            valid_moves = temp_board.get_valid_moves()
            if not valid_moves:
                return 0
                
            move = random.choice(valid_moves)
            temp_board.drop_piece(move, current_piece)
            
            current_piece = self.opponent_piece if current_piece == self.player_piece else self.player_piece

    def backpropagate(self, winner):
        self.visits += 1
        
        if winner == self.player_piece:
            self.wins += 1
        elif winner == self.opponent_piece:
            self.wins -= 1
            
        if self.parent:
            self.parent.backpropagate(winner)