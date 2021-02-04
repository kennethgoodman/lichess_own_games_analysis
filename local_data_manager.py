import os
import pickle
import logging
import io
from typing import Callable

import chess.engine
import chess.pgn

import lichess_data_manager
import lichess_to_python_chess
import add_chess_analysis

DATA_FOLDER = 'data'
logger = logging.getLogger(__name__)


def get_games_from_lichess(userid, download):
    return lichess_data_manager.get_all_games(userid, download)


def get_path_to_user_id_games(userid, analysis_time):
    analysis_prefix = "no" if analysis_time is None else str(analysis_time)
    return os.path.join(DATA_FOLDER, f'{userid}.python_chess.{analysis_prefix}_analysis.pickle')


def data_exists(userid, analysis_time):
    return os.path.exists(get_path_to_user_id_games(userid, analysis_time))


def save_data(games, userid, analysis_time):
    path = get_path_to_user_id_games(userid, analysis_time)
    games = list(games)
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(path, 'wb') as f:
        for game in games:
            pickle.dump(str(game), f)


def read_data(userid, analysis_time):
    path = get_path_to_user_id_games(userid, analysis_time)
    with open(path, 'rb') as f:
        games = []
        while True:
            try:
                loaded = pickle.load(f)
                pgn = io.StringIO(loaded)
                game = chess.pgn.read_game(pgn)
                games.append(game)
            except EOFError:
                break
        return games


def combine_berserk_and_analysis_data(userid, download, analysis_time):
    def get_new_games_data(games_data, games_lichess_dict):
        new_games = []
        for game in games_data:
            id = lichess_to_python_chess.site_to_id(game.headers['Site'])
            game_json = games_lichess_dict[id]
            new_games.append(
                lichess_to_python_chess.convert_game(
                    game_json,
                    pgn_moves_str=str(game)
                )
            )
        return new_games
    games_lichess = get_games_from_lichess(userid, download)
    games_lichess_dict = {}
    for game_json in games_lichess:
        games_lichess_dict[game_json['id']] = game_json

    games_data_without_analysis = read_data(userid, None)
    new_games_without_analysis = get_new_games_data(games_data_without_analysis, games_lichess_dict)
    save_data(new_games_without_analysis, userid, None)

    if analysis_time is not None:
        games_data_with_analysis = read_data(userid, analysis_time)
        new_games_with_analysis = get_new_games_data(games_data_with_analysis, games_lichess_dict)
        save_data(new_games_with_analysis, userid, analysis_time)
        return new_games_with_analysis
    return new_games_without_analysis


def combine_lichess_analysis_and_analysis_data(userid, download, analysis_time):
    def get_new_games_data(games_data, games_lichess_dict):
        new_games = []
        for game in games_data:
            id = lichess_to_python_chess.site_to_id(game.headers['Site'])
            game_json = games_lichess_dict[id]
            converted_game = lichess_to_python_chess.convert_game(
                game_json,
                pgn_moves_str=game_json['pgn']
            )
            if 'analysis' not in game_json:
                # got to combine clock here
                converted_game_with_self_analysis = lichess_to_python_chess.convert_game(
                    game_json,
                    pgn_moves_str=str(game)
                )
                cur_move = converted_game
                cur_move_with_self_analysis = converted_game_with_self_analysis
                i = 0
                while len(cur_move.variations) and len(cur_move_with_self_analysis.variations):
                    if i != 0:
                        # skip the first eval before any move played
                        cur_move.comment = cur_move_with_self_analysis.comment + " " + cur_move.comment
                    cur_move = cur_move.variations[0]
                    cur_move_with_self_analysis = cur_move_with_self_analysis.variations[0]
                    i += 1
            new_games.append(
                converted_game
            )
        return new_games
    games_lichess = get_games_from_lichess(userid, download)
    games_lichess_dict = {}
    for game_json in games_lichess:
        games_lichess_dict[game_json['id']] = game_json

    games_data_with_analysis = read_data(userid, analysis_time)
    new_games_with_analysis = get_new_games_data(games_data_with_analysis, games_lichess_dict)
    save_data(new_games_with_analysis, userid, analysis_time)
    return new_games_with_analysis


def get_all_games(userid, engine, download, parse, analysis_time, game_filter: Callable= None):
    if parse:
        # from `brew install stockfish`
        games = get_games_from_lichess(userid, download)
        games = lichess_to_python_chess.convert_games(games, game_filter=game_filter)
        save_data(games, userid, None)
        games = add_chess_analysis.add_eval_to_games(games, engine, analysis_time=analysis_time)
        save_data(games, userid, analysis_time)
        logger.info("saved data")
        return games
    elif analysis_time is not None:
        if data_exists(userid, analysis_time):
            return read_data(userid, analysis_time)
        games = read_data(userid, None)
        games = add_chess_analysis.add_eval_to_games(games, engine, analysis_time=analysis_time)
        save_data(games, userid, analysis_time)
        logger.info("saved data")
        return games
    raise ValueError("either parse or analysis time")


if __name__ == '__main__':
    _ = combine_lichess_analysis_and_analysis_data('chessprimes', download=False, analysis_time=0.25)
