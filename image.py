import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
from utility import get_array_hash, get_arrays_hash

class ImageUnit:
    def __init__(self):
        self.number = self._get_number()

    def _get_number(self) -> int:
        raise Exception('Not implemented')

    def from_data(data: np.ndarray, x: int, y: int) -> 'ImageUnit':
        raise Exception('Not implemented')

    def get_display_data(self, **kwargs) -> np.ndarray:
        raise Exception('Not implemented')
    
    def display(self, ax=plt, **kwargs) -> None:
        ax.imshow(self.get_display_data(**kwargs), aspect=1)
        ax.axis('off')
        if ax == plt:
            plt.show()

    def save(self, filename, **kwargs) -> None:
        plt.imshow(self.get_display_data(**kwargs), aspect=1)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(filename+'.png',dpi=300,pad_inches=0,bbox_inches='tight')

class Tile(ImageUnit):
    def __init__(self, data: np.ndarray):
        self.data = data
        super().__init__()

    def _get_number(self) -> int:
        # TODO assumes tile shape doesn't matter
        return get_array_hash(self.data)
    
    def from_data(data: np.ndarray, x: int, y: int, tile_size: Tuple[int, int]) -> 'Tile':
        shape = (tile_size[0], tile_size[1], data.shape[2])
        if x+shape[0] > data.shape[0] or y+shape[1] > data.shape[1] or x < 0 or y < 0:
            raise Exception('Tile out of range')
        tile_data = data[x:x+shape[0], y:y+shape[1]].copy()
        return Tile(tile_data)

    def get_display_data(self, **kwargs) -> np.ndarray:
        return self.data

class Pattern(ImageUnit):
    CHECK_INPUTS = True
    def __init__(self, data_array: np.ndarray, pattern_indices: np.ndarray):
        self.data_array = data_array
        self.pattern_indices = pattern_indices
        if Pattern.CHECK_INPUTS:
            if len(pattern_indices.shape) != 2 or pattern_indices.shape[1] != 2:
                raise Exception('Wrong pattern indices dimentions: should be Nx2')
            if data_array.shape[0] != pattern_indices.shape[0]:
                raise Exception('Wrong pattern/data length during pattern definition')
            for i in range(len(pattern_indices) - 1):
                f = pattern_indices[i]
                s = pattern_indices[i + 1]
                if f[0] > s[0] or (f[0] == s[0] and f[1] >= s[1]):
                    raise Exception('Pattern indices not sorted or has duplicates')
        self.repr_index = np.where(np.all(pattern_indices==np.array([0, 0]),axis=1))[0][0]
        super().__init__()

    def _get_number(self) -> int:
        return get_arrays_hash(self.data_array, self.pattern_indices)

    # x, y and pattern_indices are tile indices
    def from_data(data: np.ndarray, tile_size: Tuple[int, int], x: int, y: int, pattern_indices: np.ndarray) -> 'Pattern':
        data_array = []
        for [i, j] in pattern_indices:
            xs = (x+i)*tile_size[0]
            ys = (y+j)*tile_size[1]
            if Pattern.CHECK_INPUTS:
                if xs < 0 or xs+tile_size[0] > data.shape[0] or ys < 0 or ys+tile_size[1] > data.shape[1]:
                    raise Exception("Pattern out of range")
            data_array.append(data[xs:xs+tile_size[0], ys:ys+tile_size[1]])
        data_array = np.array(data_array)
        return Pattern(data_array, pattern_indices)

    def _get_tile(self):
        return Tile(self.data_array[self.repr_index])

    def get_display_data(self, **kwargs) -> np.ndarray:
        if 'full_pattern' not in kwargs or not kwargs['full_pattern']:
            return Tile(self.data_array[self.repr_index]).data
        else:
            tile_size = (self.data_array.shape[1], self.data_array.shape[2])
            min_x = min(self.pattern_indices[:,0])
            max_x = max(self.pattern_indices[:,0])
            min_y = min(self.pattern_indices[:,1])
            max_y = max(self.pattern_indices[:,1])
            data = np.ones(((max_x - min_x + 1)*tile_size[0], (max_y - min_y + 1)*tile_size[1], self.data_array.shape[3]), dtype=self.data_array.dtype)
            for ind, [i, j] in enumerate(self.pattern_indices):
                xs = (i-min_x)*tile_size[0]
                ys = (j-min_y)*tile_size[1]
                data[xs:xs+tile_size[0], ys:ys+tile_size[1]] = self.data_array[ind]
            return data

class nxmPattern(Pattern):
    def get_min_indices(n: int, m: int) -> Tuple[int, int]:
        #xs = - int(n/2)
        #ys = - int(m/2)
        #return xs, ys
        return 0, 0 # Gumin's implementation
      
    # x, y and n, m are tile indices/counts, not pixel indices/counts
    def from_data(data: np.ndarray, tile_size: Tuple[int, int], x: int, y: int, n: int, m: int) -> 'nxmPattern':
        min_indices = nxmPattern.get_min_indices(n, m)
        pattern_indices = np.array([[i, j] for i in range(min_indices[0], min_indices[0]+n) for j in range(min_indices[1], min_indices[1]+m)])
        return Pattern.from_data(data, tile_size, x, y, pattern_indices)

class UpLeftLPattern(Pattern): # L shaped pattern: center tile + n tiles up + m tiles left
    def get_min_indices(n: int, m: int) -> Tuple[int, int]:
        return -n, -m
    
    # x, y and n, m are tile indices/counts, not pixel indices/counts
    def from_data(data: np.ndarray, tile_size: Tuple[int, int], x: int, y: int, n: int, m: int) -> 'UpLeftLPattern':
        up_indices = np.array([[i, 0] for i in range(-n, 0)])
        left_and_center_indices = np.array([[0, j] for j in range(-m, 1)])
        pattern_indices = np.concatenate((up_indices, left_and_center_indices), axis=0)
        return Pattern.from_data(data, tile_size, x, y, pattern_indices)

# New patterns can be defined here