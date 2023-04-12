# Context-sensitive WFC

This is the code for the "Better Resemblance without Bigger Patterns: Making Context-sensitive Decisions in WFC" paper by Bahar Bateni, Isaac Karth and Adam Smith. 
The paper was published at FDG 2023 and is available at https://dl.acm.org/doi/10.1145/3582437.3582441.

![Figure_1](https://user-images.githubusercontent.com/25642714/231170868-24e1baa5-e98f-4236-ace0-d76263a730c0.png)

The paper proposes a small and easy to implement modification to the WaveFunctionCollapse algorithm which significantly improves the quality fo results.

WaveFunctionCollapse (WFC) is a Procedural Content Generation algorithm which generates an image similar to some input image. The input image is broken into tiles or patterns
which can be composed by the algorithm to create a new image. A set of constraints extracted from the input are satisfied during the process which results in the similarity
between the input and output. For more information about the WFC algorithm refer to https://github.com/mxgmn/WaveFunctionCollapse.

For more information about this modification refer to the paper. To run this code, refer to the [How to Run](#how-to-run) section. If you want to implement the context-sensitive
heuristic in your own work, refer to the [Porting Context-sensitive Heuristic](#porting-context-sensitive-heuristic) section.
To use an interactive tool and get some outputs, use the colab notebook available at [TODO add link].

## How to Run

### Requirements

The list of requirements are available in the `requirements.txt` file. You can install these requirements with `pip` by using:

```
pip install -r requirements.txt
```

It is suggested to use a virtual environment when installing the requirements. You can use virtualenv by running:

```
pip install virtualenv
virtualenv venv
[windows] venv\Scripts\activate
[linux] source venv/bin/activate
pip install -r requirements.txt
```

To learn more, refer to virtualenv documents.

### Running WFC

You can run the WFC algorithm by running the main script:

`python main.py`

This would results in generating one output per each of the *Decision Heuristic*s for the zelda example.
The result will differ each time. To get the same results everytime, change the `GLOBAL_HASH_TYPE` in the `utility.py` file:

```
GLOBAL_HASH_TYPE = HASH_TYPE.NUMBER_HASH
```

This will run a deterministic hashing algorithm which is significantly slower than the other implementation, but will remove the randomnetss and generate the same output
every time the algorithm is executed with the same seed.

### Available Options

The following options are available in the `main.py` file to get the desired outputs. The examples in the `main.py` file show how the same code can be used for bigger patterns,
as well as visualizing those patterns.

- `backtrack=False` shows if backtracking will be used for satisfying all the constraints. The default value is `False`, meaning that when there are no possible options for
a tile, that tile can be left blank (showing with a white tile). By using `backtrack=True` the execution time will significantly increase based on how limiting the constraints
are, but the result will feel all the tile positions with valid tiles.
- `weighting_option` is the heuristic which gives weights to each tile option in the *Decicion* process. For more information refer to the
[Decition Heuristic](#decision-heuristic) section.
- `entropy_option` is the heuristic which gives entropy values to each position in the *Selection* process. For more information refer to the
[Selection Heuristic](#selection-heuristic) section.

## Implementaiton

This implementation contains the following files:



### WFC's main loop

The main loop of WFC does the following:

1. Start with an empty grid of the desired size
2. Iteratively, while an empty position exists on the grid:
    1. Select an empty position on the grid (sometimes refered to as *Selection Heuristic*)
    2. Decide which one of the **valid** tiles to put in the target position (refered to as *Decision Process*)
3. Once all positions have been filled with tiles, the output has been generated and the algorithm terminates.

A tile is considered **valid** for a position if the tile is not resulting in contradiction with the available constraints. These constraints decide which pair of tiles can
appear as neighbors in the output based on if the same pair have appeared as neighbors in the input. For instance, if tile A have never been an immediate
neighbor above tile B in the input, then tile B can't be chosen for a position that has A immediately above it in the output.

### Selection Heuristics

![Figure_3](https://user-images.githubusercontent.com/25642714/231180741-ca1caaee-b6e6-4d56-84b5-08168d6a36dd.png)


### Decision Heuristics

## Porting Context-sensitive Heuristic

## FAQ

**Some tiles in the output are blank (completely white). What's wrong?**

This is because the algorithm can't find any valid tiles for those positions. Try running the algorithm with backtracking by setting `backtrack=True`. This will increase the
exection time but will search all the available options to get a valid result. If there are no valid results available, the code will return a `Not possible` exception.

**There are some artifact in the results: there is a diagonal pattern seen in the outputs. What should I do?**

This shows some bias in the output, which can be a result of selection heuristic.
