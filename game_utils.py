import io
import numpy as np
import pandas as pd
import chess
import chess.svg
import chess.pgn
import chess.engine



my_username = 'peterni'



def evaluate_board(board):
    engine = chess.engine.SimpleEngine.popen_uci('/opt/homebrew/bin/stockfish')
    info = engine.analyse(board, chess.engine.Limit(time=0.1))
    engine.quit()
    white_score = info["score"].white().score(mate_score=100000)
    black_score = info["score"].black().score(mate_score=100000)
    return white_score, black_score


def count_game_moves(game):
    move_num = 0
    for move in game.mainline_moves():
        move_num += 1
    return move_num


def white_or_black_move(moves):
    if moves % 2 == 0:
        return 0 # White
    else:
        return 1 # Black


def check_position_for_queens(board):
    white_queens = len(board.pieces(chess.QUEEN, chess.WHITE))
    black_queens = len(board.pieces(chess.QUEEN, chess.BLACK))
    if(white_queens + black_queens < 2):
        return False
    else:
        return True




def check_position_for_queen_trade(board):
    legal_moves = list(board.legal_moves)
    for move in legal_moves:
        if board.is_capture(move) and board.piece_at(move.to_square) is not None and board.piece_at(move.from_square) is not None:
            if board.piece_at(move.to_square).piece_type == chess.QUEEN and board.piece_at(move.from_square).piece_type == chess.QUEEN:
                # Simulate the move
                board.push(move)
                # Check if the other queen can be captured in return
                if can_capture_queen(board):
                    # Undo the move
                    board.pop()
                    return True
                # Undo the move
                board.pop()
    return False

def can_capture_queen(board):
    legal_moves = list(board.legal_moves)
    for move in legal_moves:
        if board.is_capture(move) and board.piece_at(move.to_square) is not None:
            if board.piece_at(move.to_square).piece_type == chess.QUEEN:
                return True
    return False


def get_first_queen_trade(game):
    # Initialize board, move number
    board = game.board()
    move_num = 1

    # For each move in input game
    for move in game.mainline_moves():

        board.push(move)        
        two_queens_on_board = check_position_for_queens(board)
        if(two_queens_on_board):
            queen_trade_possible = check_position_for_queen_trade(board)
        
        if(queen_trade_possible):
            return move_num + 1
        
        move_num += 1
    return -1



def process_one_game(game):
    if game.headers["White"] == my_username:
        my_color = 'White'
    else:
        my_color = 'Black'

    first_queen_trade = get_first_queen_trade(game)
    WhiteElo = game.headers.get("WhiteElo")
    BlackElo = game.headers.get("BlackElo")

    # Check if first_queen_trade is color's move
    if(first_queen_trade % 2 == 1):
        color_to_play = 'White'
    else:
        color_to_play = 'Black'

    # Check if color_to_play is color
    drop_game = color_to_play != my_color
    drop_game_missing_elo = WhiteElo == '?' or BlackElo == '?'


    # Check if first_queen_trade is the last move in the game
    half_move_ct = count_game_moves(game)
    if(first_queen_trade == half_move_ct + 1):
        drop_game_trade_at_end = True
    else:
        drop_game_trade_at_end = False
    

    include_game = not(drop_game or drop_game_missing_elo or drop_game_trade_at_end)
    if(include_game):
        # Initialize board
        board = game.board()
        move_ct = 1
        # Play first_queen_trade moves - 1 moves
        for move in game.mainline_moves():
            board.push(move)
            move_ct += 1
            if(move_ct == first_queen_trade):
                white_eval, black_eval = evaluate_board(board)
                if(my_color == 'White'):
                    pre_eval = white_eval
                else:
                    pre_eval = black_eval
                
                break
        # Play moves 1 through first_queen_trade moves
        move_ct = 0
        board = game.board()
        for move in game.mainline_moves():
            board.push(move)
            move_ct += 1
            if(move_ct == first_queen_trade):
                # Check if move was a queen trade
                is_capture = board.is_capture(move)
                captured_piece_is_queen = board.piece_at(move.to_square).piece_type == chess.QUEEN

                board.pop()
                attacker_piece_is_queen = board.piece_at(move.from_square).piece_type == chess.QUEEN
                board.push(move)

                if(is_capture 
                    and captured_piece_is_queen
                    and attacker_piece_is_queen):
                    queen_trade_made = True
                else:
                    queen_trade_made = False
                

                white_eval, black_eval = evaluate_board(board)
                if(my_color == 'White'):
                    post_eval = white_eval
                else:
                    post_eval = black_eval
                
                break
        
        # If game is included, make numpy array holding [WhiteElo, BlackElo, pre_eval, post_eval, queen_trade_made]

        out = np.array([WhiteElo, BlackElo, pre_eval, post_eval, queen_trade_made])
        out = pd.DataFrame(out.reshape(1, -1), columns=['WhiteElo', 'BlackElo', 'pre_eval', 'post_eval', 'queen_trade_made'])

        # Modify above to also include first_queen_trade
        out['first_queen_trade'] = first_queen_trade
        out['my_color'] = my_color
        out['result'] = game.headers.get("Result")
        return(out)

            


# Test Sandbox
# debug_pgn = '1. e4 e5 2. d4 exd4 3. Qxd4 a6 4. Be3 Qf6 5. Qxf6 gxf6 6. Nf3 f5'

# Read into game
import io
# debug_game = chess.pgn.read_game(io.StringIO(debug_pgn))
# debug_first_queen_trade = get_first_queen_trade(debug_game)
# print('First queen trade: ', debug_first_queen_trade)
# print('Moves in game: ', count_game_moves(debug_game))


# process_one_game(debug_game, 'White')

