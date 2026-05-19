from Player import Player

class MinimaxAIPlayer(Player):
    def __init__(self, piece):
        super().__init__(piece)
        
    def get_move(self, board):
        valid_moves = board.get_valid_moves()
        best_score = -float('inf')
        best_col = valid_moves[0] if valid_moves else 0

        # O oponente será a outra peça (se fores o 1, o oponente é o 2, e vice-versa)
        opponent_piece = 2 if self.piece == 1 else 1

        # Avalia a melhor jogada inicial a partir do topo da árvore
        for col in valid_moves:
            new_board = board.copy()
            new_board.drop_piece(col, self.piece)
            
            # Se esta jogada ganhar imediatamente, escolhe-a logo
            if new_board.check_winner(self.piece):
                return col
                
            score = self.minimax(new_board, self.max_depth - 1, -float('inf'), float('inf'), False)
            
            if score > best_score:
                best_score = score
                best_col = col

        return best_col

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        valid_moves = board.get_valid_moves()
        opponent_piece = 2 if self.piece == 1 else 1
        
        # Verificar estados terminais primeiro [cite: 68]
        if board.check_winner(self.piece):
            return 100000 + depth  # Valorizar vitórias mais rápidas
        if board.check_winner(opponent_piece):
            return -100000 - depth  # Penalizar derrotas mais rápidas
        if board.is_board_full() or depth == 0:
            return self.evaluate_board(board, self.piece)

        if maximizing_player:
            max_eval = -float('inf')
            for col in valid_moves:
                new_board = board.copy()
                new_board.drop_piece(col, self.piece)
                evaluation = self.minimax(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, evaluation)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break  # Poda Alpha-Beta 
            return max_eval
        else:
            min_eval = float('inf')
            for col in valid_moves:
                new_board = board.copy()
                new_board.drop_piece(col, opponent_piece)
                evaluation = self.minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, evaluation)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break  # Poda Alpha-Beta 
            return min_eval

    def evaluate_board(self, board, player):
        score = 0
        opponent = 2 if player == 1 else 1
        n = board.n_connect

        # 1. Posição no Tabuleiro: Valorizar o controlo do centro 
        center_col = board.cols // 2
        center_array = [int(i) for i in list(board.grid[:, center_col])]
        center_count = center_array.count(player)
        score += center_count * 3  # Dá 3 pontos por cada peça tua na coluna central 

        # Função auxiliar para pontuar uma "janela" de tamanho N 
        def evaluate_window(window, player, opponent, n):
            window_score = 0
            player_count = window.count(player)
            opp_count = window.count(opponent)
            empty_count = window.count(0)

            if player_count == n:
                window_score += 10000  # Vitória imediata [cite: 75]
            elif player_count == n - 1 and empty_count == 1:
                window_score += 100    # Sequência de N-1 peças com espaço livre 
            elif player_count == n - 2 and empty_count == 2:
                window_score += 10     # Sequência de N-2 peças 

            if opp_count == n - 1 and empty_count == 1:
                window_score -= 80     # Penalizar forte ameaça do adversário 
            elif opp_count == n - 2 and empty_count == 2:
                window_score -= 8      # Penalizar sequências menores do adversário [cite: 79]

            return window_score

        # 2. Avaliação Horizontal 
        for r in range(board.rows):
            row_array = [int(i) for i in list(board.grid[r, :])]
            for c in range(board.cols - n + 1):
                window = row_array[c:c+n]
                score += evaluate_window(window, player, opponent, n)

        # 3. Avaliação Vertical 
        for c in range(board.cols):
            col_array = [int(i) for i in list(board.grid[:, c])]
            for r in range(board.rows - n + 1):
                window = col_array[r:r+n]
                score += evaluate_window(window, player, opponent, n)

        # 4. Avaliação Diagonal Positiva (/) 
        for r in range(n - 1, board.rows):
            for c in range(board.cols - n + 1):
                window = [board.grid[r-i][c+i] for i in range(n)]
                score += evaluate_window(window, player, opponent, n)

        # 5. Avaliação Diagonal Negativa (\) 
        for r in range(board.rows - n + 1):
            for c in range(board.cols - n + 1):
                window = [board.grid[r+i][c+i] for i in range(n)]
                score += evaluate_window(window, player, opponent, n)

        return score
        #gaydrigo na zona
        
    
    