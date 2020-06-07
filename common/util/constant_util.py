KLINE_MIN_COLUMNS = ["amount", "count", "open", "close", "low", "high", "volumn", "timestamp", "rise_fall_num", "rise_fall_amplitude", "id"]
STABLE_UP_LOW_COLUMNS = ['symbol', 'all_count', 'count', 'stable_duration', 'max_percents', 'min_percents', 'middle_lows', 'count_2', 'count_3', 'count_5', 'count_8']
# ------ JWT ------ #
JWT_OPTIONS = {
    'verify_signature': True,
    'verify_exp': True,
    'verify_nbf': False,
    'verify_iat': True,
    'verify_aud': False
}

JWT_ALGORITHM = "HS256"

JWT_HEADERS = {
    'typ': 'jwt',
    'alg': JWT_ALGORITHM
}
# ------ JWT ------ #

