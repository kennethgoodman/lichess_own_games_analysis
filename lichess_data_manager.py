import os
import pickle
import logging

import berserk

DATA_FOLDER = 'data'
logger = logging.getLogger(__name__)

def get_games_from_lichess(userid):
    client = berserk.Client()
    return client.games.export_by_player(userid)


def get_path_to_user_id_games(userid):
    return os.path.join(DATA_FOLDER, userid + '.lichess.pickle')


def data_exists(userid):
    return os.path.exists(get_path_to_user_id_games(userid))


def save_data(games, userid):
    path = get_path_to_user_id_games(userid)
    games = list(games)
    os.makedirs(DATA_FOLDER, exist_ok=True)
    with open(path, 'wb') as f:
        pickle.dump(games, f)


def read_data(userid):
    path = get_path_to_user_id_games(userid)
    with open(path, 'rb') as f:
        return pickle.load(f)


def get_all_games(userid, download):
    if download or not data_exists(userid):
        games = get_games_from_lichess(userid)
        save_data(games, userid)
    elif data_exists(userid):
        games = read_data(userid)
    else:
        raise ValueError("if download=False then the data must exist already")
    return games


if __name__ == '__main__':
    games = get_all_games('chessprimes', download=False)
