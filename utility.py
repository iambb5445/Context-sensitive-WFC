import numpy as np

class Move:
    DOWN = (1, 0)
    UP = (-1, 0)
    RIGHT = (0, 1)
    LEFT = (0, -1)
    CCW = [DOWN, RIGHT, UP, LEFT]
    CW = [DOWN, LEFT, UP, RIGHT]

def add_to_dict(d, key, val=1):
    if key in d:
        d[key] += val
    else:
        d[key] = val

def in_bound(x: int, y: int, arr: np.ndarray):
    return x >= 0 and y >= 0 and x < arr.shape[0] and y < arr.shape[1]

class HASH_TYPE:
    PYTHON_HASH = 1 # fast, but unreliable
    # (has randomness that makes different results even with the same seed)
    # https://stackoverflow.com/questions/27522626/hash-function-in-python-3-3-returns-different-results-between-sessions
    NUMBER_HASH = 2 # slow

GLOBAL_HASH_TYPE = HASH_TYPE.PYTHON_HASH

def get_array_hash(arr):
    if GLOBAL_HASH_TYPE == HASH_TYPE.PYTHON_HASH:
        return hash(arr.tobytes())
    elif GLOBAL_HASH_TYPE == HASH_TYPE.NUMBER_HASH:
        big_prime = 1000000007
        out = 0
        r_arr = arr.reshape(-1)
        for val in r_arr:
            out *= 256
            out += round(val * 255)
            out %= big_prime
        return out
    else:
        raise Ecxeption("Unknown hash type")

def get_arrays_hash(arr1, arr2):
    if GLOBAL_HASH_TYPE == HASH_TYPE.PYTHON_HASH:
        return hash((arr1.tobytes(), arr2.tobytes()))
    elif GLOBAL_HASH_TYPE == HASH_TYPE.NUMBER_HASH:
        # not a good way, but in this case doesn't matter.
        return get_array_hash(arr1) + get_array_hash(arr2)
    else:
        raise Ecxeption("Unknown hash type")