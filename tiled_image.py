import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
from image import ImageUnit, Tile, Pattern, nxmPattern, UpLeftLPattern

class ImageUnitGenerator:
    def __init__(self, data: np.ndarray, blank: ImageUnit):
        self.data = data
        self.blank = blank

    def get_next(self) -> ImageUnit:
        raise Exception('Not implemented')
    
    def get_size(self) -> Tuple[int, int]:
        raise Exception('Not implemented')

    def get_blank(self):
        return self.blank

    def _pointer_next(self, step: Tuple[int, int], start: Tuple[int, int], end: Tuple[int, int]) -> None:
        if not hasattr(self, "pointer"):
            self.pointer = [start[0], start[1]]
            return
        if self.pointer is None:
            return
        self.pointer[1] += step[1]
        if self.pointer[1] >= end[1]:
            self.pointer[1] = start[1]
            self.pointer[0] += step[0]
        if self.pointer[0] >= end[0]:
            self.pointer = None

class TileGenerator(ImageUnitGenerator):
    def __init__(self, data: np.ndarray, tile_size: Tuple[int, int], blank: Tile=None):
        self.tile_size = tile_size
        if blank is None:
            blank = Tile(np.ones((tile_size[0], tile_size[1], data.shape[2])))
        super().__init__(data, blank)
        self.size = (int(self.data.shape[0]/self.tile_size[0]), int(self.data.shape[1]/self.tile_size[1]))

    def get_size(self) -> Tuple[int, int]:
        return self.size

    def get_next(self) -> Tile:
        start = (0, 0)
        end = (self.data.shape[0]-self.tile_size[0]+1, self.data.shape[1]-self.tile_size[1]+1)
        self._pointer_next(step=self.tile_size, start=start, end=end)
        if self.pointer is None:
            return None
        return Tile.from_data(self.data, self.pointer[0], self.pointer[1], self.tile_size)

class PatternGenerator(ImageUnitGenerator):
    def __init__(self, data: np.ndarray, tile_size: Tuple[int, int], blank: Pattern):
        self.tile_size = tile_size
        super().__init__(data, blank)
        self.size = (int(self.data.shape[0]/self.tile_size[0]), int(self.data.shape[1]/self.tile_size[1]))

    def get_size(self) -> Tuple[int, int]:
        return self.size
    
    def _pad_data(self, min_indices: Tuple[int, int], max_indices: Tuple[int, int]) -> None: #wrap around
        # assuming a valid pattern ([0, 0] in the indices)
        x_padding = (-min_indices[0]*self.tile_size[0], max_indices[0]*self.tile_size[0]) # pixel scale
        y_padding = (-min_indices[1]*self.tile_size[1], max_indices[1]*self.tile_size[1])
        padded_data = np.pad(self.data, (x_padding, y_padding, (0, 0)), mode='wrap')
        self.start_tile = [-min_indices[0], -min_indices[1]] # tile scale
        self.end_tile = [int(padded_data.shape[0]/self.tile_size[0]) - max_indices[0], int(padded_data.shape[1]/self.tile_size[1]) - max_indices[1]] # tile scale
        self.data = padded_data

class nxmPatternGenerator(PatternGenerator):
    def __init__(self, data: np.ndarray, tile_size: Tuple[int, int], n: int, m: int, blank: nxmPattern=None):
        self.n = n
        self.m = m
        if blank is None:
            blank = nxmPattern.from_data(np.ones((tile_size[0]*(2*n+1), tile_size[1]*(2*m+1), data.shape[2])), tile_size, n, m, n, m) # TODO more efficient
        super().__init__(data, tile_size, blank)
        min_indices = nxmPattern.get_min_indices(n, m)
        self._pad_data(min_indices, (min_indices[0]+n-1, min_indices[1]+m-1))
    
    def get_next(self) -> nxmPattern:
        self._pointer_next(step=(1, 1), start=self.start_tile, end=self.end_tile)
        if self.pointer is None:
            return None
        return nxmPattern.from_data(self.data, self.tile_size, self.pointer[0], self.pointer[1], self.n, self.m)

class UpLeftLPatternGenerator(PatternGenerator):
    def __init__(self, data: np.ndarray, tile_size: Tuple[int, int], n: int, m: int, blank: UpLeftLPattern=None):
        self.n = n
        self.m = m
        if blank is None:
            blank = UpLeftLPattern.from_data(np.ones((tile_size[0]*(2*n+1), tile_size[1]*(2*m+1), data.shape[2])), tile_size, n, m, n, m) # TODO more efficient
        super().__init__(data, tile_size, blank)
        min_indices = UpLeftLPattern.get_min_indices(n, m)
        self._pad_data(min_indices, (0, 0))
    
    def get_next(self) -> UpLeftLPattern:
        self._pointer_next(step=(1, 1), start=self.start_tile, end=self.end_tile)
        if self.pointer is None:
            return None
        return UpLeftLPattern.from_data(self.data, self.tile_size, self.pointer[0], self.pointer[1], self.n, self.m)

class TiledImage:
    def __init__(self, number_to_unit, unit_numbers: np.ndarray, blank: ImageUnit):
        self.number_to_unit = number_to_unit
        self.unit_numbers = unit_numbers
        self.blank = blank
        self.number_to_unit[blank.number] = blank

    def from_unit_generator(u_gen: ImageUnitGenerator) -> 'TiledImage':
        number_to_unit = {}
        size = u_gen.get_size()
        unit_numbers = np.zeros(size, dtype=np.int64)
        # not int because of possible overflow: OverflowError: Python int too large to convert to C long
        # https://stackoverflow.com/questions/38314118/overflowerror-python-int-too-large-to-convert-to-c-long-on-windows-but-not-ma
        unit = u_gen.get_next()
        pos = [0, 0]
        while unit is not None:
            if unit.number not in number_to_unit:
                number_to_unit[unit.number] = unit
            unit_numbers[(pos[0], pos[1])] = unit.number
            pos[1] += 1
            if pos[1] >= size[1]:
                pos[0] += 1
                pos[1] = 0
            unit = u_gen.get_next()
        return TiledImage(number_to_unit, unit_numbers, u_gen.get_blank())

    def from_generated(self, generated):
        number_to_unit = {}
        for i in range(generated.shape[0]):
            for j in range(generated.shape[1]):
                if generated[i, j] not in number_to_unit:
                    if generated[i, j] is None:
                        generated[i, j] = self.blank.number
                    else:
                        number_to_unit[generated[i, j]] = self.number_to_unit[generated[i, j]]
        return TiledImage(number_to_unit, generated, self.blank)

    def _from_generated_get_tiles_for_zelda(self, generated): # TODO remove this
        number_to_unit = {}
        generated_tiled = np.zeros(generated.shape, dtype=generated.dtype)
        blank = Tile(np.ones((16, 16, 3))) # for zelda, fix this
        for i in range(generated.shape[0]):
            for j in range(generated.shape[1]):
                if generated[i, j] is None:
                    generated[i, j] = blank.number
                    continue
                unit = self.number_to_unit[generated[i, j]]._get_tile()
                number = unit.number
                generated[i, j] = number
                if number not in number_to_unit:
                    number_to_unit[number] = unit
        return TiledImage(number_to_unit, generated, blank)

    def get_display_data(self, **kwargs) -> None:
        repr_datas = []
        shapes = []
        for i in range(self.unit_numbers.shape[0]):
            for j in range(self.unit_numbers.shape[1]):
                unit = self.number_to_unit[self.unit_numbers[i, j]]
                repr_datas.append(unit.get_display_data(**kwargs))
                shapes.append(repr_datas[-1].shape)
        shapes = np.array(shapes)
        x_scale = max(shapes[:, 0])
        y_scale = max(shapes[:, 1])
        data = np.zeros((x_scale*self.unit_numbers.shape[0], y_scale*self.unit_numbers.shape[1], repr_datas[0].shape[2]), dtype=repr_datas[0].dtype)
        for i in range(self.unit_numbers.shape[0]):
            for j in range(self.unit_numbers.shape[1]):
                c = i*self.unit_numbers.shape[1] + j
                data[i*x_scale:i*x_scale+shapes[c][0], j*y_scale:j*y_scale+shapes[c][1], :] = repr_datas[c]
        return data

    def display(self, ax=plt, **kwargs) -> None:
        ax.imshow(self.get_display_data(**kwargs), aspect=1)
        ax.axis('off')
        if ax == plt:
            if 'filename' in kwargs:
                plt.savefig('{}.png'.format(kwargs['filename']),dpi=300,pad_inches=0)
            plt.show()