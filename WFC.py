import numpy as np
from image_distribution import ImageDistribution
from utility import in_bound

class WeightingOptions:
    NONE = 1 # Uniform Distribution
    FREQUENCY_WEIGHTED = 2 # based on the frequency of units #Gumin's
    CONTEXT_WEIGHTED = 3 # based on the conditional prbability (conditioned by context around it)

class UpdatingOptions:
    NEIGHBOR = 1
    CHAIN = 2 #Gumin's

class EntropyOptions:
    NUMBER_OF_OPTIONS = 1
    SHANNON = 2 #Gumin's
    TOP_LEFT = 3
    TOP_RIGHT = 4

class ExistingTile:
    def __init__(self, pos, tile_number):
        self.pos = pos
        self.tile_number = tile_number
    
    def from_tile(pos, tile):
        return ExistingTile(pos, tile.number)

class WFC:
    def __init__(self, dist: ImageDistribution, weighting_option, updating_option, entropy_option):
        self.dist = dist
        self.updating_option = updating_option
        self.entropy_option = entropy_option
        self.weighting_option = weighting_option

    def _get_updated_possibilities(self, possibilities, collapsed_value, move_number):
        if possibilities.shape[0] == 1:
            return possibilities
        return possibilities[np.array(list(map(lambda p: (collapsed_value, p, move_number) in self.dist.exists, possibilities)))]

    def _get_options(self):
        return np.array(list(self.dist.unit_numbers), dtype=np.int64)
        # not int because of possible overflow: OverflowError: Python int too large to convert to C long
        # https://stackoverflow.com/questions/38314118/overflowerror-python-int-too-large-to-convert-to-c-long-on-windows-but-not-ma

    def _get_context(self, supermap, unit_number, x, y):
        context = [unit_number, None, None, None, None]
        for k in range(len(ImageDistribution.MOVESET)):
            dx, dy = ImageDistribution.MOVESET[k]
            if in_bound(x+dx, y+dy, supermap) and len(supermap[x+dx, y+dy]) == 1:
                context[k+1] = supermap[x+dx, y+dy][0]
        return (context[0], context[1], context[2], context[3], context[4])
    
    def _get_weights(self, supermap, x, y):
        if self.weighting_option == WeightingOptions.FREQUENCY_WEIGHTED:
            return np.array(list(map(lambda u: self.dist.get_unit_frequency(u), supermap[x, y])))
        elif self.weighting_option == WeightingOptions.NONE:
            return np.ones(supermap[x, y].shape)
        elif self.weighting_option == WeightingOptions.CONTEXT_WEIGHTED:
            weights = np.array(list(map(lambda u: self.dist.get_context_frequency(self._get_context(supermap, u, x, y)), supermap[x, y])))
            if np.sum(weights) == 0:
                return np.array(list(map(lambda u: self.dist.get_unit_frequency(u), supermap[x, y]))) # fall-back: return frequency weighted
            return weights
        raise Exception("weighting option not implemented!")

    def _get_probabilities(self, supermap, x, y):
        weights = self._get_weights(supermap, x, y)
        return weights/np.sum(weights)

    def _get_entropy(self, supermap, x, y, map_size):
        if self.entropy_option == EntropyOptions.SHANNON:
            weights = self._get_weights(supermap, x, y)
            return np.log(np.sum(weights)) - (np.sum(weights * np.log(weights)) / np.sum(weights))
        elif self.entropy_option == EntropyOptions.NUMBER_OF_OPTIONS:
            return len(supermap[x, y])
        elif self.entropy_option == EntropyOptions.TOP_LEFT:
            return x * map_size[1] + y
        elif self.entropy_option == EntropyOptions.TOP_RIGHT:
            return x * map_size[1] + (map_size[0] - y)
        raise Exception("entropy option not implemented!")

    def _get_position_to_collapse(self, supermap, map_size):
        entropies = []
        for i in range(supermap.shape[0]):
            for j in range(supermap.shape[1]):
                entropies.append(self._get_entropy(supermap, i, j, map_size) if len(supermap[i, j]) > 1 else np.Inf)
        entropies = np.array(entropies)
        min_entropy = np.argmin(entropies, axis=None)
        if entropies[min_entropy] == np.Inf:
            return None, None
        return np.unravel_index(np.argmin(entropies, axis=None), supermap.shape)

    def _collapse(self, supermap, x, y, map_size):
        probabilities = self._get_probabilities(supermap, x, y)
        supermap[x, y] = np.array([np.random.choice(supermap[x, y], p=probabilities)])

    def _update_supermap(self, changed_x, changed_y, supermap):
        changed_queue = [(changed_x, changed_y)]
        invalid = False
        while len(changed_queue) > 0:
            x, y = changed_queue[0]
            changed_queue = changed_queue[1:]
            if len(supermap[x, y]) != 1:
                continue # TODO WHY? -> because we need the collapsed value to get possibilities
            for k in range(len(ImageDistribution.MOVESET)):
                dx, dy = ImageDistribution.MOVESET[k]
                if in_bound(x+dx, y+dy, supermap) and len(supermap[x+dx, y+dy]) > 1:
                    new_possibilities = self._get_updated_possibilities(supermap[x+dx, y+dy], supermap[x, y][0], k)
                    if len(new_possibilities) != len(supermap[x+dx, y+dy]):
                        supermap[x+dx, y+dy] = new_possibilities
                        if len(new_possibilities) < 1:
                            invalid = True
                        if self.updating_option == UpdatingOptions.NEIGHBOR:
                            pass
                        elif self.updating_option == UpdatingOptions.CHAIN:
                            changed_queue.append((x+dx, y+dy))
        return not invalid

    def _get_initial_supermap(self, map_size): # TODO consider existing tiles
        options = self._get_options()
        supermap = np.array([[None for _ in range(map_size[1])] for _ in range(map_size[0])], dtype=object)
        for i in range(map_size[0]):
            for j in range(map_size[1]):
                supermap[i, j] = options.copy()
        return supermap

    def generate_bt(self, map_size, existing_tiles=[]):
        self._bt_counter = 0
        supermap = self._get_initial_supermap(map_size)
        tested = np.array([[None for _ in range(map_size[1])] for _ in range(map_size[0])], dtype=object)
        for i in range(map_size[0]):
            for j in range(map_size[1]):
                tested[i, j] = []
        checkpoints = [(supermap.copy(), tested.copy())]
        while True:
            if len(checkpoints) == 0:
                raise Exception('Not possible')
            # copy supermap and tested
            supermap, tested = checkpoints[-1]
            supermap, tested = supermap.copy(), tested.copy() # TODO deep copy supermap (not really needed)
            for i in range(map_size[0]):
                for j in range(map_size[1]):
                    tested[i, j] = [val for val in tested[i, j]]
            # find position to collapse
            x, y = self._get_position_to_collapse(supermap, map_size) # why not remove tested: because then maybe len == 1 for some positions
            if x is None or y is None:
               break
            #use untested ones at [x, y] to collapse(x, y)
            options = supermap.copy()
            options[x, y] = np.delete(options[x, y], np.where(np.in1d(options[x, y], tested[x, y])))
            if len(options[x, y]) == 0:
                checkpoints = checkpoints[:-1]
                continue
            if len(options[x, y]) > 1:
                self._collapse(options, x, y, map_size)
            supermap[x, y] = options[x, y]
            #update tested
            tested[x, y].append(supermap[x, y][0])
            checkpoints[-1][1][x, y].append(supermap[x, y][0])
            if self._update_supermap(x, y, supermap):
                # checkpoint
                checkpoints.append((supermap, tested))
            self._bt_counter += 1
        map = np.array([[possibilities[0] if len(possibilities) > 0 else None for possibilities in row] for row in supermap])
        return map

    def generate(self, map_size, seed=0, existing_tiles=[], backtrack=False):
        np.random.seed(seed)
        if backtrack:
            return self.generate_bt(map_size, existing_tiles)
        supermap = self._get_initial_supermap(map_size)
        while True:
            x, y = self._get_position_to_collapse(supermap, map_size)
            if x is None or y is None:
                break
            self._collapse(supermap, x, y, map_size)
            self._update_supermap(x, y, supermap)
        map = np.array([[possibilities[0] if len(possibilities) > 0 else None for possibilities in row] for row in supermap])
        return map