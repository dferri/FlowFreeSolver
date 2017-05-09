# FlowFreeSolver
Solve [Flow Free](https://play.google.com/store/apps/details?id=com.bigduckgames.flow&hl=en) puzzles from a screenshot

# Usage
Pass as argument the path to the screenshot

## Example
To get this:

![puzzle](https://i.imgur.com/kyBjaeB.jpg)

Run the command
```
python3 detect.py path/to/screenshot.png
```

## Other usage
You can detect a grid without solving it with `--no-solve`:
```
$ python3 detect.py --no-solve path/to/screenshot.png
(9, 9)
[[(1, 1), (4, 4)], [(1, 2), (2, 3)], [(1, 3), (2, 7)], [(2, 4), (2, 6)], [(3, 7), (5, 1)], [(4, 1), (4, 3)], [(5, 0), (6, 2)], [(5, 7), (7, 1)], [(5, 8), (6, 1)]]
```

# Modules
The solver is actually built on three modules:
* detect: for detecting the puzzle from an image
* solver: actually solving the puzzle using brute force
* solver_sat: actually solving the puzzle using [Z3](https://github.com/Z3Prover/z3) (recommended)


# Credits
Images and puzzles are from the [Flow Free app](https://play.google.com/store/apps/details?id=com.bigduckgames.flow&hl=en)
