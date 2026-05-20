import math
import random

from Player import Player


class MCTSAIPlayer(Player):
    """
    Agente de IA que utiliza o algoritmo Monte Carlo Tree Search (MCTS)
    implementado de raiz para jogar Connect N.
    """
    
    def __init__(self, piece, max_iterations=1000):
        """
        Inicializa o jogador MCTS.
        :param piece: Identificador da peça do jogador (ex: 1 ou 2).
        :param max_iterations: Número fixo de iterações por jogada.
        """
        super().__init__(piece)
        self.max_iterations = max_iterations
        self.opponent_piece = 2 if piece == 1 else 1

    def get_move(self, board):
        """
        Método principal da API do agente. Retorna a melhor jogada (coluna).
        :param board: Estado atual do tabuleiro (read-only).
        :return: Inteiro correspondente à coluna escolhida.
        """
        valid_moves = board.get_valid_moves()
        
        # Salvaguardas iniciais de execução rápida
        if len(valid_moves) == 1:
            return valid_moves[0]
        if not valid_moves:
            return 0

        # Criar o nó raiz que representa o estado atual do tabuleiro
        root = MCTSNode(board.copy(), player_piece=self.piece, opponent_piece=self.opponent_piece)

        # Executar o número fixo de iterações exigido pelo enunciado
        for _ in range(self.max_iterations):
            node = root
            
            # 1. SELEÇÃO: Navegar usando a fórmula UCB1
            while node.is_fully_expanded() and not node.is_terminal():
                node = node.best_child_ucb()

            # 2. EXPANSÃO: Adicionar um novo nó filho à árvore
            if not node.is_terminal():
                node = node.expand()

            # 3. SIMULAÇÃO / ROLLOUT: Jogo aleatório até ao fim
            winner = node.simulate()

            # 4. RETROPROPAGAÇÃO / BACKPROPAGATION: Atualizar estatísticas subindo a árvore
            node.backpropagate(winner)

        # A jogada final escolhida é o movimento do nó filho que foi MAIS VISITADO
        best_child = max(root.children.values(), key=lambda c: c.visits)
        return best_child.move_that_led_here


class MCTSNode:
    """
    Classe auxiliar interna para representar cada nó da árvore de procura do MCTS.
    """
    def __init__(self, board, parent=None, move_that_led_here=None, player_piece=1, opponent_piece=2):
        self.board = board  # Estado do tabuleiro neste nó
        self.parent = parent  # Nó pai
        self.move_that_led_here = move_that_led_here  # A coluna que gerou este nó
        
        self.player_piece = player_piece
        self.opponent_piece = opponent_piece
        
        # Dicionário para guardar os nós filhos: { coluna: MCTSNode }
        self.children = {}
        
        # Lista de jogadas válidas que ainda não foram testadas a partir deste nó
        self.untried_moves = board.get_valid_moves()
        
        # Estatísticas necessárias para a fórmula UCB1
        self.visits = 0
        self.wins = 0

    def is_terminal(self):
        """ Retorna True se o jogo terminou neste nó (vitória de alguém ou empate). """
        return (self.board.check_winner(self.player_piece) or 
                self.board.check_winner(self.opponent_piece) or 
                self.board.is_board_full())

    def is_fully_expanded(self):
        """ Retorna True se todas as jogadas possíveis a partir deste nó já foram expandidas. """
        return len(self.untried_moves) == 0

    def expand(self):
        """ Fase de Expansão: Retira uma jogada não testada, cria o nó filho e retorna-o. """
        move = self.untried_moves.pop()
        next_board = self.board.copy()
        
        # Descobrir de quem é a vez de jogar neste nível da árvore para colocar a peça correta
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
        """ Função auxiliar para alternar os turnos corretamente ao longo da árvore. """
        depth = 0
        p = self
        while p.parent is not None:
            depth += 1
            p = p.parent
        return depth % 2 == 0

    def best_child_ucb(self, exploration_constant=1.414):
        """ Fase de Seleção: Escolhe o nó filho maximizando a fórmula UCB1. """
        best_score = -math.inf
        best_children = []
        
        for child in self.children.values():
            # Fórmula UCB1 clássica: Explotação + Exploration
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
        """ Fase de Simulação (Rollout): Joga aleatoriamente a partir deste estado até ao fim do jogo. """
        temp_board = self.board.copy()
        
        # Define quem deve fazer a primeira jogada na simulação aleatória
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
            
            # Alternar o jogador dentro da simulação aleatória
            current_piece = self.opponent_piece if current_piece == self.player_piece else self.player_piece

    def backpropagate(self, winner):
        """ Fase de Retropropagação: Sobe de volta até à raiz atualizando os scores. """
        self.visits += 1
        
        # Vitória dá +1 crédito, derrota penaliza com -1, empate é neutro (0)
        if winner == self.player_piece:
            self.wins += 1
        elif winner == self.opponent_piece:
            self.wins -= 1
            
        if self.parent:
            self.parent.backpropagate(winner)