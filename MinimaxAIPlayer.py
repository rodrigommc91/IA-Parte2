import math
import random 

from Player import Player

# Nota: Garante que a classe Player está disponível ou importada corretamente
# conforme a estrutura dos ficheiros do teu projeto.
class MinimaxAIPlayer(Player):
    """
    Agente de IA que utiliza o algoritmo Minimax com Poda Alpha-Beta
    e uma função heurística para jogar Connect N.
    """
    
    def __init__(self, piece, max_depth=4):
        """
        Inicializa o jogador Minimax.
        :param piece: Identificador da peça do jogador (ex: 1 ou 2).
        :param max_depth: Profundidade máxima fixa para a pesquisa na árvore.
        """
        self.piece = piece
        self.max_depth = max_depth
        # O adversário terá o número oposto (assumindo peças 1 e 2)
        self.opponent_piece = 2 if piece == 1 else 1

    def get_move(self, board):
        """
        Método principal da API do agente. Retorna a melhor jogada (coluna).
        :param board: Estado atual do tabuleiro (read-only).
        :return: Inteiro correspondente à coluna escolhida.
        """
        valid_moves = board.get_valid_moves()
        
        # Salvaguarda: se apenas houver uma jogada possível, joga imediatamente
        if len(valid_moves) == 1:
            return valid_moves[0]
            
        best_score = -math.inf
        best_move = valid_moves[0] if valid_moves else 0
        
        # Início da procura adversarial com Alpha-Beta (Nível Max inicial)
        alpha = -math.inf
        beta = math.inf
        
        for col in valid_moves:
            # Criar uma cópia do tabuleiro para simular a jogada (obrigatório pela API)
            next_board = board.copy()
            next_board.drop_piece(col, self.piece)
            
            # Chamar o nível Min (adversário) na profundidade seguinte
            score = self._minimax(next_board, 1, False, alpha, beta)
            
            if score > best_score:
                best_score = score
                best_move = col
                
            alpha = max(alpha, best_score)
            
        return best_move

    def _minimax(self, board, depth, is_maximizing, alpha, beta):
        """
        Função auxiliar interna que executa o algoritmo recursivo Minimax com Poda Alpha-Beta.
        """
        # 1. Verificação de estados terminais (Casos Base)
        if board.check_winner(self.piece):
            return 100000 - depth  # Valorizar vitórias mais rápidas
        if board.check_winner(self.opponent_piece):
            return -100000 + depth  # Penalizar derrotas mais rápidas
        if board.is_board_full():
            return 0  # Empate tem valor neutro
            
        # Se atingiu a profundidade máxima, avalia o estado atual usando a heurística
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
                    break  # Poda Alpha
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
                    break  # Poda Beta
            return min_eval

    @staticmethod
    def evaluate_board(game, player):
        """
        Função heurística obrigatória para avaliar o estado do tabuleiro.
        Pontua sequências benéficas e penaliza ameaças.
        
        Assinatura exata exigida pelo enunciado: evaluate_board(game, player)
        """
        score = 0
        grid = game.grid
        rows = len(grid)
        cols = len(grid[0])
        opponent = 2 if player == 1 else 1
        
        # 1. Pontuar Posição Central
        center_col = cols // 2
        center_array = [grid[r][center_col] for r in range(rows)]
        center_count = center_array.count(player)
        score += center_count * 3

        # 2. Avaliação de Alinhamentos (Janelas de 4 posições consecutivas)
        # Horizontal
        for r in range(rows):
            for c in range(cols - 3):
                window = [grid[r][c+i] for i in range(4)]
                score += MinimaxAIPlayer._score_window(window, player, opponent)

        # Vertical
        for c in range(cols):
            for r in range(rows - 3):
                window = [grid[r+i][c] for i in range(4)]
                score += MinimaxAIPlayer._score_window(window, player, opponent)

        # Diagonal Positiva (/)
        for r in range(rows - 3):
            for c in range(cols - 3):
                window = [grid[r+i][c+i] for i in range(4)]
                score += MinimaxAIPlayer._score_window(window, player, opponent)

        # Diagonal Negativa (\)
        for r in range(3, rows):
            for c in range(cols - 3):
                window = [grid[r-i][c+i] for i in range(4)]
                score += MinimaxAIPlayer._score_window(window, player, opponent)

        return score

    @staticmethod
    def _score_window(window, player, opponent):
        """
        Função auxiliar estática para classificar uma 'janela' de 4 posições.
        """
        score = 0
        player_count = window.count(player)
        opponent_count = window.count(opponent)
        empty_count = window.count(0) # Assumindo que 0 representa posições vazias

        # Pontuar sequências do próprio jogador (2 e 3 peças)
        if player_count == 3 and empty_count == 1:
            score += 50
        elif player_count == 2 and empty_count == 2:
            score += 10

        # Penalizar/Bloquear ameaças do adversário (peso maior para evitar derrota iminente)
        if opponent_count == 3 and empty_count == 1:
            score -= 80
        elif opponent_count == 2 and empty_count == 2:
            score -= 15

        return score     