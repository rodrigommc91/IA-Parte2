import math
import random 

from Player import Player

class MinimaxAIPlayer(Player):
    
    def __init__(self, piece, max_depth=4):
        
        self.piece = piece
        self.max_depth = max_depth
        self.opponent_piece = 2 if piece == 1 else 1

    def get_move(self, board):
        
        valid_moves = board.get_valid_moves()
        
        if len(valid_moves) == 1:
            return valid_moves[0]
            
        best_score = -math.inf
        best_move = valid_moves[0] if valid_moves else 0
        
        alpha = -math.inf
        beta = math.inf
        
        for col in valid_moves:
            next_board = board.copy()
            next_board.drop_piece(col, self.piece)
            
            score = self._minimax(next_board, 1, False, alpha, beta)
            
            if score > best_score:
                best_score = score
                best_move = col
                
            alpha = max(alpha, best_score)
            
        return best_move

    def _minimax(self, board, depth, is_maximizing, alpha, beta):
        
        if board.check_winner(self.piece):
            return 100000 - depth 
        if board.check_winner(self.opponent_piece):
            return -100000 + depth 
        if board.is_board_full():
            return 0 
            
        if depth == self.max_depth:
            return MinimaxAIPlayer.evaluate_board(board, self.piece)
            
        valid_moves = board.get_valid_moves()
        
        if is_maximizing:
            max_eval = -math.inf
            for col in valid_moves:
                next_board = board.copy()
                next_board.drop_piece(col, self.piece)
                evaluation = self._minimax(next_board, depth + 1, False, alpha, beta)
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    break 
            return max_eval
        else:
            min_eval = math.inf
            for col in valid_moves:
                next_board = board.copy()
                next_board.drop_piece(col, self.opponent_piece)
                evaluation = self._minimax(next_board, depth + 1, True, alpha, beta)
                min_eval = min(min_eval, evaluation)
                beta = min(beta, min_eval)
                if beta <= alpha:
                    break  
            return min_eval

    @staticmethod
    def evaluate_board(game, player):
        
        score = 0
        grid = game.grid
        rows = len(grid)
        cols = len(grid[0])
        opponent = 2 if player == 1 else 1
        
        center_col = cols // 2
        center_array = [grid[r][center_col] for r in range(rows)]
        center_count = center_array.count(player)
        score += center_count * 3

        for r in range(rows):
            for c in range(cols - 3):
                window = [grid[r][c+i] for i in range(4)]
                score += MinimaxAIPlayer._score_window(window, player, opponent)

        for c in range(cols):
            for r in range(rows - 3):
                window = [grid[r+i][c] for i in range(4)]
                score += MinimaxAIPlayer._score_window(window, player, opponent)

        for r in range(rows - 3):
            for c in range(cols - 3):
                window = [grid[r+i][c+i] for i in range(4)]
                score += MinimaxAIPlayer._score_window(window, player, opponent)

        for r in range(3, rows):
            for c in range(cols - 3):
                window = [grid[r-i][c+i] for i in range(4)]
                score += MinimaxAIPlayer._score_window(window, player, opponent)

        return score

    @staticmethod
    def _score_window(window, player, opponent):
        
        score = 0
        player_count = window.count(player)
        opponent_count = window.count(opponent)
        empty_count = window.count(0)

        if player_count == 3 and empty_count == 1:
            score += 50
        elif player_count == 2 and empty_count == 2:
            score += 10

        if opponent_count == 3 and empty_count == 1:
            score -= 80
        elif opponent_count == 2 and empty_count == 2:
            score -= 15

        return score     