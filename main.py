from local_data_manager import get_all_games
from logging_config import init_logger

import chess.engine


def get_engine():
    return chess.engine.SimpleEngine.popen_uci("/usr/local/Cellar/stockfish/12/bin/stockfish")


if __name__ == '__main__':
    init_logger()
    with get_engine() as engine:  # to automatically close
        games = get_all_games('chessprimes', engine, download=False, parse=False, analysis_time=0.25)
    print("games saved, goodbye")
