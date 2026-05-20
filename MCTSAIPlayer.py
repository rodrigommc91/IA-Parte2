import math
import random
from player import Player

class MCTSNode:
    def __init__(self, board, parent=None, move=None, player_turn=None):
        self.board = board                
        self.parent = parent              
        self.move = move                  
        self.player_turn = player_turn    
        self.children = {}                
        self.wins = 0.0                   
        self.visits = 0                   

    def is_fully_expanded(self):
        valid_moves = self.board.get_valid_moves()
        if not valid_moves:
            return True
        return len(self.children) == len(valid_moves)

    def get_ucb1(self, exploration_constant=1.414): # Formula UCB1 [cite: 84]
        if self.visits == 0:
            return float('inf') 
        return (self.wins / self.visits) + exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)


class MCTSAIPlayer(Player):
    def __init__(self, piece, max_iterations=500):
        super().__init__(piece)
        self.max_iterations = max_iterations # Número fixo de iterações [cite: 91, 92]

    def get_move(self, board):
        opponent_piece = 2 if self.piece == 1 else 1
        
        # Inicializa o nó raiz com o estado atual do jogo
        root = MCTSNode(board=board.copy(), player_turn=self.piece)

        for _ in range(self.max_iterations): # Ciclo principal [cite: 91, 93]
            node = root

            # 1. FASE DE SELEÇÃO [cite: 84]
            while node.is_fully_expanded() and node.children:
                if node.board.check_winner(self.piece) or \
                   node.board.check_winner(opponent_piece) or \
                   node.board.is_board_full():
                    break
                node = max(node.children.values(), key=lambda c: c.get_ucb1())

            is_terminal = node.board.check_winner(self.piece) or \
                          node.board.check_winner(opponent_piece) or \
                          node.board.is_board_full()

            # 2. FASE DE EXPANSÃO [cite: 85]
            if not is_terminal and not node.is_fully_expanded():
                valid_moves = node.board.get_valid_moves()
                unexpanded_moves = [m for m in valid_moves if m not in node.children]
                if unexpanded_moves:
                    move = random.choice(unexpanded_moves)
                    next_board = node.board.copy()
                    next_board.drop_piece(move, node.player_turn)
                    
                    next_turn = opponent_piece if node.player_turn == self.piece else self.piece
                    child_node = MCTSNode(board=next_board, parent=node, move=move, player_turn=next_turn)
                    node.children[move] = child_node
                    node = child_node

            # 3. FASE DE SIMULAÇÃO (Playout aleatório) [cite: 86]
            sim_board = node.board.copy()
            current_sim_turn = node.player_turn
            
            while not (sim_board.check_winner(self.piece) or \
                       sim_board.check_winner(opponent_piece) or \
                       sim_board.is_board_full()):
                sim_moves = sim_board.get_valid_moves()
                if not sim_moves:
                    break
                sim_move = random.choice(sim_moves)
                sim_board.drop_piece(sim_move, current_sim_turn)
                current_sim_turn = opponent_piece if current_sim_turn == self.piece else self.piece

            # Avaliação do resultado final
            if sim_board.check_winner(self.piece):
                winner = self.piece
            elif sim_board.check_winner(opponent_piece):
                winner = opponent_piece
            else:
                winner = None 

            # 4. FASE DE RETROPROPAGAÇÃO [cite: 86, 94]
            curr = node
            while curr is not None:
                curr.visits += 1
                
                if winner is None:
                    curr.wins += 0.5  # Empate recebe valor neutro [cite: 96]
                else:
                    # Identifica qual o jogador que efetuou a ação para alcançar este nó
                    who_just_played = opponent_piece if curr.player_turn == self.piece else self.piece
                    if winner == who_just_played:
                        curr.wins += 1.0  # Vitória dá crédito ao jogador [cite: 95]
                    else:
                        curr.wins += 0.0
                        
                curr = curr.parent

        if not root.children:
            valid_moves = board.get_valid_moves()
            return random.choice(valid_moves) if valid_moves else 0
            
        # Decisão final baseia-se no nó mais robusto (mais visitado)
        best_move = max(root.children.items(), key=lambda item: item[1].visits)[0]
        return best_move