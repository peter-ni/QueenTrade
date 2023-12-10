import numpy as np
import pandas as pd
import chess.pgn
import chess.svg


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import game_utils
from game_utils import get_first_queen_trade, process_one_game


chess_data_file_path = 'lichess_peterni_2023-12-08.pgn'
all_games = []


with open(chess_data_file_path) as pgn_file:
    while True:
        game = chess.pgn.read_game(pgn_file)
        if game is None:
            break
        all_games.append(game)




# Subset games into games as white and games as black
username = 'peterni'
games_as_white = []
games_as_black = []
for game in all_games:
    if game.headers["White"] == username:
        games_as_white.append(game)
    else:
        games_as_black.append(game)




# Data Import Loop


# Initialize np array to hold get_first_queen_trade results for each game in games_as_white
first_queen_trades_white = np.zeros(len(games_as_white))
first_queen_trades_black = np.zeros(len(games_as_black))


# Get white games that have queen trades
game_ct = 1
for game in games_as_white:
    first_queen_trade = get_first_queen_trade(game)
    first_queen_trades_white[game_ct-1] = first_queen_trade

    print('Queen trade possible at move {} --- Finished game: {}/{}'.format(first_queen_trade, game_ct, len(games_as_white)))
    game_ct += 1


# Get black games that have queen trades
game_ct = 1
for game in games_as_black:
    first_queen_trade = get_first_queen_trade(game)
    first_queen_trades_black[game_ct-1] = first_queen_trade

    print('Queen trade possible at move {} --- Finished game: {}/{}'.format(first_queen_trade, game_ct, len(games_as_black)))
    game_ct += 1


# Get IDX of games that have queen trades
white_game_idx = np.where(first_queen_trades_white != -1)[0]
black_game_idx = np.where(first_queen_trades_black != -1)[0]

# Extract games that have queen trades based on IDX
white_games_with_queen_trades = [games_as_white[i] for i in white_game_idx]
black_games_with_queen_trades = [games_as_black[i] for i in black_game_idx]


# Initialize pandas dataframe to hold white game data


print('==========================================')
print('Test Starts Here:')
print('==========================================')
white_set = white_games_with_queen_trades
black_set = black_games_with_queen_trades

# Initialize empty dataframe to hold white game data
white_df = pd.DataFrame(columns=['WhiteElo', 'BlackElo', 'pre_eval', 'post_eval', 'queen_trade_made',])
black_df = pd.DataFrame(columns=['WhiteElo', 'BlackElo', 'pre_eval', 'post_eval', 'queen_trade_made'])

ctx = 1
for game in white_set:
    temp_row = process_one_game(game)
    if(temp_row is not None):
        white_df = white_df.append(temp_row, ignore_index=True)

    print('Finished game: {}/{}'.format(ctx, len(white_set)))
    ctx += 1

ctx = 1
for game in black_set:
    temp_row = process_one_game(game)
    if(temp_row is not None):
        black_df = black_df.append(temp_row, ignore_index=True)

    print('Finished game: {}/{}'.format(ctx, len(black_set)))
    ctx += 1



# Save white_df to csv
white_df.to_csv('white_df.csv', index=False)
black_df.to_csv('black_df.csv', index=False)




