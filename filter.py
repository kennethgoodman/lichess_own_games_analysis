def AND(*filters):
    return lambda game: all(
        f(game) for f in filters
    )


def OR(*filters):
    return lambda game: any(
        f(game) for f in filters
    )


def filter_if_played_against_ai():
    return lambda game_json: 'aiLevel' in game_json['players']['white'] or 'aiLevel' in game_json['players']['black']


def filter_if_anonymous_player():
    return lambda game_json: 'user' not in game_json['players']['white'] or 'user' not in game_json['players']['white']


def filter_if_variant_is_not_in(*args):
    return lambda game_json: any(game_json['variant'] == arg for arg in args)


def filter_if_not_rated_game():
    return lambda game_json: not game_json['rated']
