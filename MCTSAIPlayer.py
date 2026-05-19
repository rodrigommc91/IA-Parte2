import math
import random
from Player import Player

class MCTSNode:
    def __init__(self, board, parent=None, move=None, player_turn=None):
        self.board = board                # O estado do tabuleiro neste nó
        self.parent = parent              # Nó pai
        self.move = move                  # A jogada (coluna) que levou a este nó
        self.player_turn = player_turn    # De quem é a vez de jogar NESTE nó
        self.children = {}                # Dicionário de jogada -> MCTSNode
        self.wins = 0.0                   # Pontuação de vitórias acumuladas
        self.visits = 0                   # Número de vezes que o nó foi visitado

    def is_fully_expanded(self):
        valid_moves = self.board.get_valid_moves()
        return len(self.children) == len(valid_moves)

    def get_ucb1(self, exploration_constant=1.414):
        if self.visits == 0:
            return float('inf') # Garante que nós não visitados são escolhidos primeiro
        return (self.wins / self.visits) + exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)


class MCTSAIPlayer(Player):
    def __init__(self, piece, max_iterations=500):
        super().__init__(piece)
        self.max_iterations = max_iterations

    def get_move(self, board):
        # O oponente é a outra peça
        opponent_piece = 2 if self.piece == 1 else 1
        
        # Cria a raiz da árvore para a situação atual (é a nossa vez de jogar)
        root = MCTSNode(board=board.copy(), player_turn=self.piece)

        # Loop principal das iterações do MCTS
        for _ in range(self.max_iterations):
            node = root

            # 1. SELECÇÃO: Navega usando UCB1 enquanto o nó estiver totalmente expandido
            while node.is_fully_expanded() and node.children:
                node = max(node.children.values(), key=lambda c: c.get_ucb1())

            # 2. EXPANSÃO: Se o jogo não acabou, expande um nó filho com uma jogada não testada
            valid_moves = node.board.get_valid_moves()
            
            # Verificar se o estado atual já é fim de jogo
            is_terminal = node.board.check_winner(self.piece) or \
                          node.board.check_winner(opponent_piece) or \
                          node.board.is_board_full()

            if not is_terminal and not node.is_fully_expanded():
                unexpanded_moves = [m for m in valid_moves if m not in node.children]
                if unexpanded_moves:
                    move = random.choice(unexpanded_moves)
                    next_board = node.board.copy()
                    next_board.drop_piece(move, node.player_turn)
                    
                    # Alterna o turno para o próximo nó filho
                    next_turn = opponent_piece if node.player_turn == self.piece else self.piece
                    child_node = MCTSNode(board=next_board, parent=node, move=move, player_turn=next_turn)
                    node.children[move] = child_node
                    node = child_node

            # 3. SIMULAÇÃO (Playout): Corre uma partida aleatória a partir deste estado
            sim_board = node.board.copy()
            current_sim_turn = node.player_turn
            
            while not (sim_board.check_winner(self.piece) or 
                       sim_board.check_winner(opponent_piece) or 
                       sim_board.is_board_full()):
                sim_moves = sim_board.get_valid_moves()
                if not sim_moves:
                    break
                sim_move = random.choice(sim_moves)
                sim_board.drop_piece(sim_move, current_sim_turn)
                current_sim_turn = opponent_piece if current_sim_turn == self.piece else self.piece

            # Determinar o resultado para a retropropagação
            if sim_board.check_winner(self.piece):
                reward = 1.0       # Ganhámos nós
            elif sim_board.check_winner(opponent_piece):
                reward = 0.0       # Ganhou o adversário
            else:
                reward = 0.5       # Empate (valor neutro conforme enunciado)

            # 4. RETROPROPAGAÇÃO (Backpropagation): Sobe a árvore e atualiza as estatísticas
            while node is not None:
                node.visits += 1
                # Como os turnos alternam, o "crédito" deve fazer sentido para quem jogou na transição
                # Mas de forma simples: se o pai do nó atual tomou a decisão que levou a uma vitória nossa,
                # valorizamos os nós corretos. Uma abordagem robusta é creditar a recompensa se o nó anterior foi nosso.
                node.wins += reward
                node = node.parent

        # No fim de todas as iterações, escolhemos a jogada mais robusta (a que foi MAIS VISITADA)
        if not root.children:
            return random.choice(board.get_valid_moves())
            
        best_move = max(root.children.items(), key=lambda item: item[1].visits)[0]
        return best_move