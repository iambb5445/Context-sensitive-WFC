from utility import Move, in_bound, add_to_dict

class ImageDistribution:
    MOVESET = Move.CCW
    def __init__(self):
        self.unit_frequency = {}
        self.pair_frequency = [{} for _ in ImageDistribution.MOVESET]
        self.pair_dir_frequency = {}
        self.context_frequency = {}
        self.unit_frequency_sorted = []
        self.pair_frequency_sorted = [[] for _ in ImageDistribution.MOVESET]
        self.pair_dir_frequency_sorted = []
        self.context_frequency_sorted = []
        self.exists = set()
        self.unit_numbers = set()
    
    def train(self, tiled_image):
        self._train_unit_frequency(tiled_image)
        self._train_pair_frequency(tiled_image)
        self._train_context_frequency(tiled_image)

    def get_unit_frequency(self, unit):
        return self.unit_frequency.get(unit, 0)

    def get_context_frequency(self, context):
        return self.context_frequency.get(context, 0)

    def _train_unit_frequency(self, tiled_image):
        units = tiled_image.unit_numbers
        for i in range(units.shape[0]):
            for j in range(units.shape[1]):
                add_to_dict(self.unit_frequency, units[i, j])
                self.unit_numbers.add(units[i, j])
        self.unit_frequency_sorted = sorted(list(self.unit_frequency.items()), key=lambda keyvalue: -keyvalue[1])
    
    def _train_pair_frequency(self, tiled_image):
        units = tiled_image.unit_numbers
        for i in range(units.shape[0]):
            for j in range(units.shape[1]):
                for k in range(len(ImageDistribution.MOVESET)):
                    dx, dy = ImageDistribution.MOVESET[k]
                    if in_bound(i+dx, j+dy, units):
                        add_to_dict(self.pair_frequency[k], (units[i, j], units[i+dx, j+dy]))
                        add_to_dict(self.pair_dir_frequency, (units[i, j], units[i+dx, j+dy], k))
                        self.exists.add((units[i, j], units[i+dx, j+dy], k))
              
        for k in range(len(ImageDistribution.MOVESET)):
            self.pair_frequency_sorted[k] = sorted(list(self.pair_frequency[k].items()), key=lambda keyvalue: -keyvalue[1])
        self.pair_dir_frequency_sorted = sorted(list(self.pair_dir_frequency.items()), key=lambda keyvalue: -keyvalue[1])

    def _train_context_frequency(self, tiled_image):
        units = tiled_image.unit_numbers
        for i in range(units.shape[0]):
            for j in range(units.shape[1]):
                context = [units[i, j], None, None, None, None]
                for k in range(len(ImageDistribution.MOVESET)):
                    dx, dy = ImageDistribution.MOVESET[k]
                    if in_bound(i+dx, j+dy, units):
                        context[k+1] = units[i+dx, j+dy]
                # TODO None senario probably won't happen at all
                for e1 in range(1 if context[1] is None else 2):
                    for e2 in range(1 if context[2] is None else 2):
                        for e3 in range(1 if context[3] is None else 2):
                            for e4 in range(1 if context[4] is None else 2):
                                context_key = (units[i, j],
                                              None if e1 == 1 else context[1],
                                              None if e2 == 1 else context[2],
                                              None if e3 == 1 else context[3],
                                              None if e4 == 1 else context[4])
                                add_to_dict(self.context_frequency, context_key)
        self.context_frequency_sorted = sorted(list(self.context_frequency.items()), key=lambda keyvalue: -keyvalue[1])