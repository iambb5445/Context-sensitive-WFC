import numpy as np
import imageio.v2 as imageio
import matplotlib.pyplot as plt
from tiled_image import TiledImage, TileGenerator, nxmPatternGenerator, UpLeftLPatternGenerator
from WFC import EntropyOptions, WeightingOptions, UpdatingOptions, WFC
from image_distribution import ImageDistribution
from utility import GifMaker

def get_stick_data():
    arr = np.ones((7, 7, 3)) * 0.4
    arr[1, 3] = 0.9
    arr[2, 3] = 0.9
    arr[3, 3] = 0.9
    arr[4, 3] = 0.9
    arr[5, 3] = 0.9
    return arr

def get_image_data(filename):
    im = imageio.imread(filename)
    arr = np.asarray(im)/255
    return arr

def visualize_tile_vs_pattern(image_data, tile_size, pattern_generator_func):
    n, m, _ = image_data.shape
    if n % tile_size[0] != 0 or m % tile_size[1] != 0:
        print("Warning: the data is not divisible by the tile size, not all of the data is shown.")
    n = round(n / tile_size[0])
    m = round(m / tile_size[1])
    ti = TiledImage.from_unit_generator(TileGenerator(image_data, tile_size))
    # _, axs = plt.subplots(nrows=1, ncols=1, figsize=(5, 5))
    # ti.display(axs)
    _, axs = plt.subplots(nrows=n, ncols=2*m+1, figsize=(2*m+1, n))
    for i in range(n):
        for j in range(m):
            ti.number_to_unit[ti.unit_numbers[i, j]].display(axs[i, j])
            ti.blank.display(axs[i, 9])
    ti = TiledImage.from_unit_generator(pattern_generator_func(image_data, tile_size))
    for i in range(n):
        for j in range(m):
            ti.number_to_unit[ti.unit_numbers[i, j]].display(axs[i, j+m+1], full_pattern=True)
    for i in range(n):
        for j in range(2*m+1):
            axs[i, j].axis("off")
    plt.show()


def visualize_wfc_decision_heuristics(unit_generator, size, seed=42, backtrack=False, axs=None,
                                 entropy_option=EntropyOptions.TOP_LEFT, updating_option=UpdatingOptions.CHAIN):
    print("breaking input into tiles...")
    ti = TiledImage.from_unit_generator(unit_generator)
    if axs is None:
        _, axs = plt.subplots(nrows=1, ncols=4, figsize=(16, 4))
    axs[0].set_title('Source', fontsize=22)
    ti.display(axs[0])
    print("training the distribution...")
    id = ImageDistribution()
    id.train(ti)
    print("running wfc with uniform decision heuristic...")
    axs[1].set_title('Uniform', fontsize=22)
    wfc = WFC(id, WeightingOptions.UNIFORM, updating_option, entropy_option)
    ti.from_generated(wfc.generate(size, seed=seed, backtrack=backtrack)).display(axs[1])
    print("running wfc with tile-frequency decision heuristic...")
    axs[2].set_title('Tile Frequency', fontsize=22)
    wfc = WFC(id, WeightingOptions.TILE_FREQUENCY, updating_option, entropy_option)
    ti.from_generated(wfc.generate(size, seed=seed, backtrack=backtrack)).display(axs[2])
    print("running wfc with context-sensitive decision heuristic...")
    axs[3].set_title('Context-sensitive', fontsize=22)
    wfc = WFC(id, WeightingOptions.CONTEXT_SENSITIVE, updating_option, entropy_option)
    ti.from_generated(wfc.generate(size, seed=seed, backtrack=backtrack)).display(axs[3])
    plt.show()

def visualize_wfc_selection_heuristics(unit_generator, size, seed=42, backtrack=False, axs=None,
                                 weighting_option=WeightingOptions.UNIFORM, updating_option=UpdatingOptions.CHAIN):
    print("breaking input into tiles...")
    ti = TiledImage.from_unit_generator(unit_generator)
    if axs is None:
        _, axs = plt.subplots(nrows=1, ncols=5, figsize=(20, 4))
    axs[0].set_title('Source', fontsize=22)
    ti.display(axs[0])
    print("training the distribution...")
    id = ImageDistribution()
    id.train(ti)
    print("running wfc with top-left to bottom-right selection heuristic...")
    axs[1].set_title('Top-Left', fontsize=15)
    wfc = WFC(id, weighting_option, updating_option, EntropyOptions.TOP_LEFT)
    ti.from_generated(wfc.generate(size, seed=seed, backtrack=backtrack)).display(axs[1])
    print("running wfc with top-right to bottom-left selection heuristic...")
    axs[2].set_title('Top-right', fontsize=15)
    wfc = WFC(id, weighting_option, updating_option, EntropyOptions.TOP_RIGHT)
    ti.from_generated(wfc.generate(size, seed=seed, backtrack=backtrack)).display(axs[2])
    print("running wfc with number of options selection heuristic...")
    axs[3].set_title('Number of Options', fontsize=15)
    wfc = WFC(id, weighting_option, updating_option, EntropyOptions.NUMBER_OF_OPTIONS)
    ti.from_generated(wfc.generate(size, seed=seed, backtrack=backtrack)).display(axs[3])
    print("running wfc with shannon entropy selection heuristic...")
    axs[4].set_title('Shannon Entropy', fontsize=15)
    wfc = WFC(id, weighting_option, updating_option, EntropyOptions.SHANNON)
    ti.from_generated(wfc.generate(size, seed=seed, backtrack=backtrack)).display(axs[4])
    plt.show()

def visualize_single_wfc(unit_generator, size, seed=42, backtrack=False, weighting_option=WeightingOptions.UNIFORM,
                        entropy_option=EntropyOptions.TOP_LEFT, updating_option=UpdatingOptions.CHAIN):
    print("breaking input into tiles...")
    ti = TiledImage.from_unit_generator(unit_generator)
    decision_str = 'Uniform' if weighting_option==WeightingOptions.UNIFORM else\
        'Tile Frequency' if weighting_option==WeightingOptions.TILE_FREQUENCY else\
        'Context-sensitive' if weighting_option==WeightingOptions.CONTEXT_SENSITIVE else 'UNKNOWN'
    selection_str = 'Top-left' if entropy_option==EntropyOptions.TOP_LEFT else\
        'Top-right' if entropy_option==EntropyOptions.TOP_RIGHT else\
        'Number-of-options' if entropy_option==EntropyOptions.NUMBER_OF_OPTIONS else\
        'Shannon' if entropy_option==EntropyOptions.SHANNON else 'UNKNOWN'
    plt.title(f'WFC - {decision_str} Decision and {selection_str} Selection Heuristic', fontsize=15)
    print("training the distribution...")
    id = ImageDistribution()
    id.train(ti)
    print("running wfc...")
    wfc = WFC(id, weighting_option, updating_option, entropy_option)
    ti.from_generated(wfc.generate(size, seed=seed, backtrack=backtrack)).display()
    plt.show()

def save_wfc_gif(unit_generator, size, gif_name, seed=42, backtrack=False, weighting_option=WeightingOptions.UNIFORM,
                entropy_option=EntropyOptions.TOP_LEFT, updating_option=UpdatingOptions.CHAIN,  
                fps=24, repeat=False, is_gif_weighted=True):
    print("breaking input into tiles...")
    ti = TiledImage.from_unit_generator(unit_generator)
    print("training the distribution...")
    id = ImageDistribution()
    id.train(ti)
    print("running wfc in creating the gif frames...")
    wfc = WFC(id, weighting_option, updating_option, entropy_option)
    gm = GifMaker(wfc, ti, is_gif_weighted)
    wfc.generate(size, seed=seed, backtrack=backtrack, gif_maker=gm)
    print("saving the gif...")
    gm.save_gif(gif_name, fps=fps, repeat=repeat)

def main():
    stick_data = get_stick_data()
    stick_tile_size = (1, 1) # each tile is 1x1 pixels
    zelda_data = get_image_data('zeldaMap.png')
    zelda_tile_size = (16, 16) # each tile is 16x16 pixels

    output_size = (20, 20)

    ### Comparing Decition Heuristics
    # to compare decision heuristics, use:
    #>>> visualize_wfc_decision_heuristics(TileGenerator(zelda_data, zelda_tile_size), output_size,
    #>>>                                    backtrack=True, entropy_option=EntropyOptions.NUMBER_OF_OPTIONS)
    # this will generate an output containing source image and the output of running WFC with each decision heuristic
    # the other options (selection heuristic, backtrack, etc.) are the same for all of the outputs
    # for alternative types of output, refer to # Other Types of Output

    ### Bigger patterns
    # this can be slow because of exponential growth in the number of options in bigger patterns
    # e.g. zelda example has 90 tiles, but over 2900 3x3 patterns
    # to avoid generating white tiles, refere to ### Backtrack Option
    # 3x3 patterns
    #>>> visualize_wfc_decision_heuristics(nxmPatternGenerator(zelda_data, zelda_tile_size, 3, 3), output_size)
    # L shape patterns
    #>>> visualize_wfc_decision_heuristics(UpLeftLPatternGenerator(zelda_data, zelda_tile_size, 3, 3), output_size)

    # to see how the patterns look like, you can run something like this:
    # in this example, we are showing part of zelda data as both 3x3 patterns and tiles. 16x16 is the tile size in the zelda example.
    # 3x3 patterns
    #>>> visualize_tile_vs_pattern(zelda_data[16*45:16*50, 16*84:16*89], zelda_tile_size,
    #>>>                    lambda data, tile_size: nxmPatternGenerator(data, tile_size, 3, 3))
    # L shape patterns
    #>>> visualize_tile_vs_pattern(zelda_data[16*45:16*50, 16*84:16*89], zelda_tile_size,
    #>>>                    lambda data, tile_size: UpLeftLPatternGenerator(data, tile_size, 3, 3))
    
    # Other options:

    ### Backtrack Option
    # white tiles in the output show contradictions
    # at some point, there were no possible tile option left for that position due to the the existing constraints
    # you can use backtracking by adding backtrack=True to gurantee an output without missing tiles
    # this will increase the execution time significantly, specially for bigger patterns
    # example:
    #>>> visualize_wfc_decision_heuristics(TileGenerator(zelda_data, zelda_tile_size), output_size, backtrack=True)

    ### Entropy Option
    # the output might have tile regions going from top left to bottom right
    # this is specially apparent when generating bigger grids - e.g. generating 100x100 intstaed of 20x20
    # this is due to selection heuristic, in which the tiles are selected in order from top left to bottom right
    # it creates biasses in the result that can be solved with using another selection heuristic
    # such as using shannon entropy for selecting a tile position
    # example:
    #>>> visualize_wfc_decision_heuristics(TileGenerator(zelda_data, zelda_tile_size), output_size, entropy_option=EntropyOptions.SHANNON)
    # to better visualize the different between entropy options, refer to ### Comparing Selection Heuristics

    # Other Types of Output:

    ### Gif Output
    # you can use the save_wfc_gif function to get gif outputs
    # this will take some time, around a minute for each of the example below
    # all the options are till availabe (backtrack, entropy/selection heuristic, decision heuristic, etc)
    #>>> save_wfc_gif(TileGenerator(zelda_data, zelda_tile_size), output_size, 'Uniform', repeat=True,
    #>>>             backtrack=True, entropy_option=EntropyOptions.NUMBER_OF_OPTIONS, weighting_option=WeightingOptions.UNIFORM)
    #>>>
    #>>> save_wfc_gif(TileGenerator(zelda_data, zelda_tile_size), output_size, 'Tile Frequency', repeat=True,
    #>>>             backtrack=True, entropy_option=EntropyOptions.NUMBER_OF_OPTIONS, weighting_option=WeightingOptions.TILE_FREQUENCY)
    #>>>
    #>>> save_wfc_gif(TileGenerator(zelda_data, zelda_tile_size), output_size, 'Context-sensitive', repeat=True,
    #>>>             backtrack=True, entropy_option=EntropyOptions.NUMBER_OF_OPTIONS, weighting_option=WeightingOptions.CONTEXT_SENSITIVE)

    # Comparing Selection Heuristics
    # to compare selection heuristics, use:
    #>>> visualize_wfc_selection_heuristics(TileGenerator(zelda_data, zelda_tile_size), output_size, backtrack=True, weighting_option=WeightingOptions.CONTEXT_SENSITIVE)
    # this will generate an output containing source image and the output of running WFC with each selection heuristic
    # the other options (decision heuristic, backtrack, etc.) are the same for all of the outputs

    # visualizing a single output
    #>>> visualize_single_wfc(TileGenerator(zelda_data, zelda_tile_size), output_size, backtrack=True)



if __name__ == "__main__":
    main()
