from typing import List, Tuple, Dict, Union
import logging
import time

import chess.pgn
import chess.engine

logger = logging.getLogger(__name__)


def get_score(board, engine, analysis_time=0.1) -> Tuple[str, chess.engine.Score]:
    info = engine.analyse(board, chess.engine.Limit(time=analysis_time))
    pov_score: chess.engine.PovScore = info['score']
    score_from_white: chess.engine.Score = pov_score.pov(chess.WHITE)
    if isinstance(score_from_white, chess.engine.Cp):
        # in centipawn, so +41 becomes 0.41
        s = score_from_white.score() / 100.
        return f"+{s}" if s > 0.0 else str(s), score_from_white
    return str(score_from_white), score_from_white  # otherwise its mate or mate is already given


def add_eval_to_game(game: chess.pgn.Game, engine: chess.engine.SimpleEngine, analysis_time: float,
                     should_re_add_analysis: bool = False) -> chess.pgn.Game:
    """
    MODIFIES "game" IN PLACE
    """
    current_move = game
    while len(current_move.variations):
        if "eval" in current_move.comment and not should_re_add_analysis:
            continue
        score, actual_eval = get_score(current_move.board(), engine, analysis_time=analysis_time)
        current_move.comment += f'[%eval {score}]'
        if current_move.eval().pov(chess.WHITE) != actual_eval:
            # assert not rounding error
            assert abs(current_move.eval().pov(chess.WHITE).score() - actual_eval.score()) == 1, \
                f"eval's not equal, not rounding error: {current_move.eval().pov(chess.WHITE)} != {actual_eval}"
        current_move = current_move.variations[0]
    return game


def add_eval_to_games(games: List[chess.pgn.Game], engine: chess.engine.SimpleEngine, analysis_time) -> List[
    chess.pgn.Game]:
    """
    MODIFIES "game" IN PLACE
    """
    start = time.time()
    for i in range(len(games)):
        games[i] = add_eval_to_game(games[i], engine, analysis_time=analysis_time)
        total_elapses_so_far = time.time() - start
        expected_time = total_elapses_so_far * (len(games) / (i + 1))
        if i % 10 == 0:
            logger.info(f"done analysis for {i} games out of {len(games)} ({round(round(i / len(games), 3) * 100, 3)}%), "
                        f"should take expected {expected_time / 60} minutes "
                        f"or around {round(expected_time / 3600, 2)} hours. "
                        f"Time left is around {expected_time / 60 * (1 - i / len(games))} minutes")
    return games
