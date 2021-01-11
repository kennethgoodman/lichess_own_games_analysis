import local_data_manager
from logging_config import init_logger

import chess.engine


def get_engine():
    return chess.engine.SimpleEngine.popen_uci("/usr/local/Cellar/stockfish/12/bin/stockfish")


if __name__ == '__main__':
    init_logger()
    USER_ID = 'chessprimes'
    # with get_engine() as engine:  # to automatically close
    #     games = local_data_manager.get_all_games(userid=USER_ID, engine=engine, download=False, parse=False, analysis_time=0.25)
    # print("games saved, goodbye")
    local_data_manager.combine_berserk_and_analysis_data(userid=USER_ID, download=False, analysis_time=0.25)
