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
        raise Exception("Unknown hash type")

def get_arrays_hash(arr1, arr2):
    if GLOBAL_HASH_TYPE == HASH_TYPE.PYTHON_HASH:
        return hash((arr1.tobytes(), arr2.tobytes()))
    elif GLOBAL_HASH_TYPE == HASH_TYPE.NUMBER_HASH:
        # not a good way, but in this case doesn't matter.
        return get_array_hash(arr1) + get_array_hash(arr2)
    else:
        raise Exception("Unknown hash type")


class GifMaker:
    def __init__(self, wfc, tiled_image, is_weighted=True):
        self.tiled_image = tiled_image
        self.is_weighted = is_weighted
        self.wfc = wfc
        self.frames = []

    def add_frame(self, supermap):
        unit_shape = self.tiled_image.blank.get_display_data().shape
        frame = np.array([[[0.0 for _ in range(unit_shape[2])]
                                for _ in range(len(supermap[0]) * unit_shape[1])]
                                for _ in range(len(supermap) * unit_shape[0])])
        for i, row in enumerate(supermap):
            for j, options in enumerate(row):
                if not self.is_weighted:
                    probs = np.ones(options.shape) / len(options)
                else:
                    probs = self.wfc._get_probabilities(supermap, i, j)
                for k, option in enumerate(options):
                    data = np.array(self.tiled_image.number_to_unit[option].get_display_data())
                    frame[i*unit_shape[0]:(i+1)*unit_shape[0], j*unit_shape[1]:(j+1)*unit_shape[1]] += data * probs[k]
        self.frames.append((frame * 255).astype(np.uint8))

    def save_gif(self, gif_name, fps=24, repeat=False):
        import imageio
        imageio.mimsave(f'./{gif_name}.gif',
                        self.frames,
                        fps = fps,
                        loop = 0 if repeat else 1)