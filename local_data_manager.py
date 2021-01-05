import os
import pickle
import logging
import io

import chess.engine
import chess.pgn

import lichess_data_manager
import berserk_to_python_chess
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


def get_all_games(userid, engine, download, parse, analysis_time=0.05):
    if parse:
        # from `brew install stockfish`
        games = get_games_from_lichess(userid, download)
        games = berserk_to_python_chess.convert_games(games)
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
    _ = get_all_games('chessprimes', download=False, parse=True, analysis_time=0.01)
