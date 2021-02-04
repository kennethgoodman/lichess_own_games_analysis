from typing import Union, List, Callable
import io
import logging
import time

import chess.pgn

logger = logging.getLogger(__name__)

LICHESS_DOT_ORG = 'https://lichess.org/'


def site_to_id(site_str: str) -> str:
    return site_str.replace(LICHESS_DOT_ORG, "")


def id_to_site(id: str) -> str:
    return LICHESS_DOT_ORG + id


def convert_game(game_json: dict, pgn_moves_str: Union[str, None] = None, game_filter: Callable = None) -> Union[chess.pgn.Game, None]:
    """
    :param game_json: from berserk
    example:
        'id': 'bB1gKq4J',
        'rated': True,
        'variant': 'standard',
        'speed': 'blitz',
        'perf': 'blitz',
        'createdAt': datetime.datetime(2021, 1, 4, 1, 38, 27, 561000, tzinfo=datetime.timezone.utc),
        'lastMoveAt': datetime.datetime(2021, 1, 4, 1, 49, 16, 54000, tzinfo=datetime.timezone.utc),
        'status': 'draw',
        'players': {
            'white': {
                'user': {
                    'name': 'Staana12',
                    'id': 'staana12'
                },
            'rating': 1901,
            'ratingDiff': 0
            },
            'black': {
                'user': {
                    'name': 'chessprimes',
                    'id': 'chessprimes'
                },
                'rating': 1928,
                'ratingDiff': 0
            }
        },
        'moves': 'd4 d5 Bf4 Nf6 Nf3 ...',
        'clock': {'initial': 180, 'increment': 2, 'totalTime': 260}
    }
    :param pgn_moves_str: a string for the pgn, can be used to override the one from json
    :param game_filter: a filter to filter out games
    :return: chess.pgn.Game
    """
    if game_filter(game_json):
        logger.info(f"skipping {game_json} because filter evaluated as true")
        return None
    if pgn_moves_str is None:
        pgn_moves_str = game_json['pgn']
    pgn = io.StringIO(pgn_moves_str)
    try:
        game = chess.pgn.read_game(pgn)
    except ValueError as ve:
        logger.error(f"had an error parsing: {game_json} with {ve}")
        return None
    game.headers['ID'] = game_json['id']
    game.headers['Status'] = game_json['status']
    game.headers['ClockInitial'] = str(game_json['clock']['initial'])
    game.headers['ClockIncr'] = str(game_json['clock']['increment'])
    game.headers['ClockTotal'] = str(game_json['clock']['totalTime'])
    game.headers['Speed'] = game_json['speed']
    game.headers['Perf'] = game_json['perf']
    game.headers['opening'] = game_json['opening']
    # TODO: if there is analysis, those variations should be added as well
    return game


def convert_games(game_jsons: List[dict], game_filter: Callable = None) -> List[chess.pgn.Game]:
    games = []
    start = time.time()
    for i, game_json in enumerate(game_jsons):
        game = convert_game(game_json, game_filter=game_filter)
        if game is not None:
            games.append(game)
        if i % 10 == 0 and i != 0:
            total_elapses_so_far = time.time() - start
            expected_time = total_elapses_so_far * (len(game_jsons) / (i + 1))
            logger.info(f"done converting {i} games out of {len(game_jsons)} ({i / len(game_jsons)}%), "
                        f"should take expected {expected_time / 60} minutes")
    return games
