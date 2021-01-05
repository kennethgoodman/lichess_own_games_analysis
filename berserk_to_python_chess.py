from typing import Union, List
import io
import logging
import time

import chess.pgn

logger = logging.getLogger(__name__)


def convert_game(game_json: dict) -> Union[chess.pgn.Game, None]:
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
    :return: chess.pgn.Game
    """
    pgn = io.StringIO(game_json['moves'])
    if 'aiLevel' in game_json['players']['white'] or 'aiLevel' in game_json['players']['black']:
        logger.warning(f"skipping {game_json} because ailevel in players")
        return None
    if 'user' not in game_json['players']['white'] or 'user' not in game_json['players']['white']:
        logger.warning(f"skipping {game_json} because anonymous user")
        return None  # some anonymous other user, going to ignore for now
    if game_json['variant'] != 'standard':
        logger.warning(f"skipping {game_json} not standard chess")
        return None  # for non standard, not worth analyzing
    if not game_json['rated']:
        logger.warning(f"skipping {game_json} not rated chess")
        return None  # for non rated, not worth analyzing
    try:
        game = chess.pgn.read_game(pgn)
    except ValueError as ve:
        logger.error(f"had an error parsing: {game_json} with {ve}")
        return None
    game.headers['Site'] = 'https://lichess.org/' + game_json['id']
    game.headers['Date'] = game_json['createdAt']
    game.headers['White'] = game_json['players']['white']['user']['id']
    game.headers['Black'] = game_json['players']['black']['user']['id']
    return game


def convert_games(game_jsons: List[dict]) -> List[chess.pgn.Game]:
    games = []
    start = time.time()
    for i, game_json in enumerate(game_jsons):
        game = convert_game(game_json)
        if game is not None:
            games.append(game)
        if i % 10 == 0 and i != 0:
            total_elapses_so_far = time.time() - start
            expected_time = total_elapses_so_far * (len(game_jsons) / (i + 1))
            logger.info(f"done converting {i} games out of {len(game_jsons)} ({i / len(game_jsons)}%), "
                        f"should take expected {expected_time / 60} minutes")
    return games
