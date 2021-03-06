import local_data_manager
from logging_config import init_logger
from filter import (
    AND, filter_if_not_rated_game, filter_if_anonymous_player,
    filter_if_played_against_ai, filter_if_variant_is_not_in
)

import chess.engine


def get_engine():
    return chess.engine.SimpleEngine.popen_uci("/usr/local/Cellar/stockfish/12/bin/stockfish")


if __name__ == '__main__':
    init_logger()
    USER_ID = 'chessprimes'
    # TODO: add partial downloading to update new games
    SHOULD_DOWNLOAD_FROM_LICHESS = False  # true if you haven't downloaded yet or want to redownload
    # TODO: add partial parsing to update new games
    SHOULD_PARSE_DOWNLOADED_GAMES = True  # true if you haven't parsed yet or want to parse
    # TODO: add partial analysis to update new games, or update specific positions
    # TODO: add multi-engine support for averaging multiple engines
    # TODO: add quick and long analysis if not converging for speed up for simple positions (ie: mate in 5)
    ENGINE_ANALYSIS_TIME = None  # 0.25  # in seconds
    with get_engine() as engine:  # to automatically close
        games = local_data_manager.get_all_games(
            userid=USER_ID,
            engine=engine,
            download=SHOULD_DOWNLOAD_FROM_LICHESS,
            parse=SHOULD_PARSE_DOWNLOADED_GAMES,
            analysis_time=ENGINE_ANALYSIS_TIME,
            game_filter=AND(
                filter_if_not_rated_game(),
                filter_if_anonymous_player(),
                filter_if_played_against_ai(),
                filter_if_variant_is_not_in('standard')
            )
        )
    print("games saved, goodbye")
    # local_data_manager.combine_berserk_and_analysis_data(userid=USER_ID, download=False, analysis_time=0.25)
