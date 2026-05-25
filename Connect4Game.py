import pygame

from Connect4Board import Connect4Board
from Connect4Gui import Connect4Gui
from HumanPlayer import HumanPlayer
from RandomPlayer import RandomAIPlayer



# =========================
# GAME LOOP
# =========================

class Connect4Game:

    def __init__(self):
        pass

    def run_game(self, player1, player2, headless = False, rows = 6, cols = 7, n_connect = 4 ):

        board = Connect4Board(rows, cols, n_connect)

        gui = Connect4Gui(board,rows,cols)
        if (not headless):
            gui.init(board)

        players = [player1, player2]
        turn = 0
        game_over = False

        while not game_over:
            current_player = players[turn]
            if (not headless):
                gui.deal_with_events(board, current_player)

            move = current_player.get_move(board)

            if move is not None and move in board.get_valid_moves():
                row, col = board.drop_piece(move, current_player.piece)

                if board.check_winner(current_player.piece):
                    if(not headless):
                       gui.update_winner(current_player)
                    else:
                        print(f"Player {current_player.piece} wins!")

                    game_over = True

                elif board.is_board_full():
                    if (not headless):
                        gui.draw_game()
                    print("Drwa!!!!")
                    game_over = True

                if(not headless):
                    gui.draw_board(board)
                turn = (turn + 1) % 2

            # AI delay (optional for visibility)
            if not headless and not isinstance(current_player, HumanPlayer):
                pygame.time.wait(300)

            if game_over and not headless:
                gui.game_over()


# =========================
# RUN CONFIGURATION
# =========================

if __name__ == "__main__":
    import time
    from MCTSAIPlayer import MCTSAIPlayer
    from MinimaxAIPlayer import MinimaxAIPlayer
    from RandomPlayer import RandomAIPlayer 
    
    game = Connect4Game()
    
    #escolha de jogo para teste
    
    opcao_teste = "6" 
    
    if opcao_teste == "1":
        nome_linha = "Minimax vs Aleatório"
        p1 = MinimaxAIPlayer(piece=1, max_depth=4)
        p2 = RandomAIPlayer(piece=2)
    elif opcao_teste == "2":
        nome_linha = "MCTS vs Aleatório"
        p1 = MCTSAIPlayer(piece=1, max_iterations=500)
        p2 = RandomAIPlayer(piece=2)
    elif opcao_teste == "3":
        nome_linha = "1ª comb Minimax vs MCTS"
        p1 = MinimaxAIPlayer(piece=1, max_depth=2)
        p2 = MCTSAIPlayer(piece=2, max_iterations=100)
    elif opcao_teste == "4":
        nome_linha = "2ª comb Minimax vs MCTS"
        p1 = MinimaxAIPlayer(piece=1, max_depth=4)
        p2 = MCTSAIPlayer(piece=2, max_iterations=500)
    elif opcao_teste == "5":
        nome_linha = "3ª comb Minimax vs MCTS"
        p1 = MinimaxAIPlayer(piece=1, max_depth=5)
        p2 = MCTSAIPlayer(piece=2, max_iterations=1000)   
    elif opcao_teste == "6":
        nome_linha = "Humano vs IA"
        p1 = HumanPlayer(piece=1)                     
        p2 = MinimaxAIPlayer(piece=2, max_depth=4)        
    else:
        print("Opção Inválida! Escolha de 1 a 6.")
        exit()

    total_jogos = 10
    duracoes = []
    vitorias_j1 = 0  
    vitorias_j2 = 0  
    empates = 0
    
    vencedor_da_ronda = [None] 
    funcao_original_winner = Connect4Gui.update_winner
    funcao_original_draw = Connect4Gui.draw_game

    # para forçar a GUI a desenhar "Jogador 1" ou "Jogador 2"
    def espia_update_winner(self_gui, player):
        vencedor_da_ronda[0] = player.piece
        
        peca_original = player.piece
        
        if (peca_original == 1 and player == p1) or (peca_original == 2 and player == p1):
            player.piece = "Jogador 1"
        else:
            player.piece = "Jogador 2"
            
        funcao_original_winner(self_gui, player)
        
        player.piece = peca_original

    def espia_draw_game(self_gui):
        vencedor_da_ronda[0] = 0
        funcao_original_draw(self_gui)

    Connect4Gui.update_winner = espia_update_winner
    Connect4Gui.draw_game = espia_draw_game

    print(f"A executar torneio: {nome_linha.upper()}")
    
    for i in range(total_jogos):
        print(f"-> A iniciar Partida {i+1} de {total_jogos}...")
        vencedor_da_ronda[0] = None  
        
        tempo_inicio = time.time()
        
        if i % 2 == 0:
            p1.piece = 1
            p2.piece = 2
            game.run_game(p1, p2, headless=False)
            
            resultado = vencedor_da_ronda[0]
            if resultado == 1:     
                vitorias_j1 += 1
                print(f"Resultado Partida {i+1}: Vitória do Jogador 1 ({p1.__class__.__name__})")
            elif resultado == 2:   
                vitorias_j2 += 1
                print(f"Resultado Partida {i+1}: Vitória do Jogador 2 ({p2.__class__.__name__})")
            elif resultado == 0:
                empates += 1
                print(f"Resultado Partida {i+1}: Empate")
            else:
                empates += 1
                print(f"Resultado Partida {i+1}: Janela fechada")
                
        else:
            p2.piece = 1
            p1.piece = 2
            game.run_game(p2, p1, headless=False)
            
            resultado = vencedor_da_ronda[0]
            if resultado == 1:   
                vitorias_j2 += 1
                print(f"Resultado Partida {i+1}: Vitória do Jogador 2 ({p2.__class__.__name__})")
            elif resultado == 2:  
                vitorias_j1 += 1
                print(f"Resultado Partida {i+1}: Vitória do Jogador 1 ({p1.__class__.__name__})")
            elif resultado == 0:
                empates += 1
                print(f"Resultado Partida {i+1}: Empate")
            else:
                empates += 1
                print(f"Resultado Partida {i+1}: Janela fechada")
        
        tempo_fim = time.time()
        duracao_partida = tempo_fim - tempo_inicio
        duracoes.append(duracao_partida)
        print(f"Duração: {duracao_partida:.2f}s\n----------------------------------------")
        
    Connect4Gui.update_winner = funcao_original_winner
    Connect4Gui.draw_game = funcao_original_draw

    duracao_media = sum(duracoes) / len(duracoes)
    duracao_maxima = max(duracoes)
    duracao_minima = min(duracoes)
    
    taxa_vitorias_j1 = (vitorias_j1 / total_jogos) * 100
    taxa_vitorias_j2 = (vitorias_j2 / total_jogos) * 100
    
    print("Resultados ")
    print(f"Nº de Jogos:                {total_jogos}")
    print(f"Vitórias Jogador 1 (Esq):   {vitorias_j1}")
    print(f"Vitórias Jogador 2 (Dir):   {vitorias_j2}")
    print(f"Empates:                    {empates}")
    print(f"Taxa de Vitórias Jogador 1: {taxa_vitorias_j1:.1f}%")
    print(f"Taxa de Vitórias Jogador 2: {taxa_vitorias_j2:.1f}%")
    print(f"Duração Média do Jogo:      {duracao_media:.2f}s")
    print(f"Duração Máxima:             {duracao_maxima:.2f}s")
    print(f"Duração Mínima:             {duracao_minima:.2f}s")
    print("Fim.")