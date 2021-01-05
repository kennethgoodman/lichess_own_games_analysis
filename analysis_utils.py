import chess.pgn
import chess.engine


def get_move(game: chess.pgn.Game, move_num: int) -> chess.pgn.GameNode:
    i = 0
    current_game = game
    while len(current_game.variations) and i != move_num:
        i += 1
        current_game = current_game.variations[0]
    return current_game


def get_first_move_with_bad_move(game: chess.pgn.Game, player_to_follow: str, min_rating=-float('inf'), max_rating=float('inf')):
    current_move = game
    i = 0
    if game.headers['White'] == player_to_follow:
        color_following = chess.WHITE
    elif game.headers['Black'] == player_to_follow:
        color_following = chess.BLACK
    else:
        raise ValueError(f"white ({game.headers['white']}) or black ({game.headers['black']}) isn't {player_to_follow}")
    last_eval: chess.engine.Score = chess.engine.Cp(0)
    while len(current_move.variations):
        i += 1
        current_move: chess.pgn.GameNode = current_move.variations[0]
        if (color_following == chess.WHITE and i % 2 == 0) or \
           (color_following == chess.BLACK and i % 2 == 1):
            # if playing white, then eval white's moves, and visa versa
            # so lets get eval on opponents turn and
            if current_move.eval() is None:
                return i, None
            last_eval = current_move.eval().pov(color_following)
            continue
        eval: chess.engine.PovScore = current_move.eval()
        if eval is None:
            return i, None  # log it
        score_following: chess.engine.Score = eval.pov(color_following)
        if isinstance(last_eval, (chess.engine.Mate, chess.engine.MateGivenType)):
            if isinstance(score_following, (chess.engine.Mate, chess.engine.MateGivenType)):
                continue
            return i, float('inf')  # I had mate and missed it
        if isinstance(score_following, chess.engine.Mate):
            # if it wasn't mate after their move, it must be that I put myself into a mating trap
            return i, float('inf')
        score: int = score_following.score()
        difference_in_eval: int = last_eval.score() - score
        if min_rating < score < max_rating:
            # after my move in a neutral position
            if max_rating < last_eval.score():
                return i, difference_in_eval  # if was in a good position before the move
        elif score < min_rating:
            # after my move in a bad position
            return i, difference_in_eval  # in a bad position, so just return
    return i, 0.0


def get_all_losses_for_my_moves(game: chess.pgn.Game, player_to_follow: str):
    current_move = game
    i = 0
    if game.headers['White'] == player_to_follow:
        color_following = chess.WHITE
    elif game.headers['Black'] == player_to_follow:
        color_following = chess.BLACK
    else:
        raise ValueError(f"white ({game.headers['white']}) or black ({game.headers['black']}) isn't {player_to_follow}")
    last_eval: chess.engine.Score = chess.engine.Cp(0)
    while len(current_move.variations):
        i += 1
        current_move: chess.pgn.GameNode = current_move.variations[0]
        if (color_following == chess.WHITE and i % 2 == 0) or \
           (color_following == chess.BLACK and i % 2 == 1):
            # if playing white, then eval white's moves, and visa versa
            # so lets get eval on opponents turn and
            if current_move.eval() is None:
                return
            last_eval = current_move.eval().pov(color_following)
            continue
        eval: chess.engine.PovScore = current_move.eval()
        if eval is None:
            return
        score_following: chess.engine.Score = eval.pov(color_following)
        if isinstance(last_eval, (chess.engine.Mate, chess.engine.MateGivenType)):
            if isinstance(score_following, (chess.engine.Mate, chess.engine.MateGivenType)):
                yield i, 0  # zero loss if was in mate, currently in mate
            else:
                yield i, float('inf')  # I had mate and missed it
            continue
        if isinstance(score_following, chess.engine.Mate):
            # if it wasn't mate after their move, it must be that I put myself into a mating trap
            yield i, float('inf')
            continue
        score: int = score_following.score()
        difference_in_eval: int = last_eval.score() - score
        yield i, difference_in_eval
    return
