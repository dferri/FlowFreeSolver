#!/usr/bin/env python3
import copy
from z3 import *

# Initialize z3
z3.init("/usr/lib/python3.6/site-packages/z3")

LEVEL_SIZE = (5, 5)
INPUT = [[(0, 0), (4, 1)], [(0, 2), (3, 1)], [(0, 4), (3, 3)], [(1, 2), (4, 2)], [(1, 4), (4, 3)]]

def print_grid(grid):
    for l in grid:
        print(" ".join(["{:3}".format(i) if i >= 0 else "   " for i in l]))

def solve_sat(grid_start, size):
    """Solves the puzzle using Z3"""
    r, c = Ints("r c")
    rows, cols = size
    n = len(grid_start)
    grid = Function("grid", IntSort(), IntSort(), IntSort())
    # # z3.solve(f(f(x)) == x, f(x) == y, x!=y)
    s = Solver()
    # s.add(ForAll([r, c], f(r, c) >  0))

    # Defined only inside the grid and values in the right range
    s.add(ForAll([r, c], Implies(And(r >= 0, r < rows,
                                     c >= 0, c < cols),
                                 And(grid(r, c) >= 0,
                                     grid(r, c) < n))))
    s.add(ForAll([r, c], Implies(Or(r < 0, r >= size[0],
                                    c < 0, c >= size[1]),
                                 grid(r, c) == -1)))
    print(grid_start)
    for i, ((x1, y1), (x2, y2)) in enumerate(grid_start):
        s.add(grid(x1, y1) == i)
        s.add(grid(x2, y2) == i)
    # Other constraints
    # Top
    # s.add(ForAll([r, c],
    #              Implies(And(r > 0, c > 0, c < h - 1),
    #                      Not(And(grid(r, c)
    #                              == grid(r-1, c-1)
    #                              == grid(r-1, c)
    #                              == grid(r-1, c+1))))))
    # DEEEEBUUUG
    # solution = [[0, 1, 1, 2, 2], [0, 1, 3, 2, 4], [0, 1, 3, 2, 4], [0, 1, 3, 2, 4], [0, 0, 3, 4, 4]]
    # for i, row in enumerate(solution):
    #     for j, pup in enumerate(row):
    #         s.add(grid(i, j) == pup)


    # Top
    s.add(ForAll([r, c],
                 Implies(And(r > 0, r < rows, c > 0, c < cols - 1),
                         Not(And(grid(r, c) == grid(r-1, c-1),
                                 grid(r, c) == grid(r-1, c),
                                 grid(r, c) == grid(r-1, c+1))))))
    # Top Right
    s.add(ForAll([r, c],
                 Implies(And(r > 0, r < rows, c >= 0, c < cols - 1),
                         Not(And(grid(r, c) == grid(r-1, c),
                                 grid(r, c) == grid(r-1, c+1),
                                 grid(r, c) == grid(r, c+1))))))
    # Right
    s.add(ForAll([r, c],
                 Implies(And(r > 0, r < rows - 1, c >= 0, c < cols - 1),
                         Not(And(grid(r, c) == grid(r-1, c+1),
                                 grid(r, c) == grid(r, c+1),
                                 grid(r, c) == grid(r+1, c+1))))))
    # Bottom Right
    s.add(ForAll([r, c],
                 Implies(And(r >= 0, r < rows - 1, c >= 0, c < cols - 1),
                         Not(And(grid(r, c) == grid(r, c+1),
                                 grid(r, c) == grid(r+1, c+1),
                                 grid(r, c) == grid(r+1, c))))))
    # Bottom
    s.add(ForAll([r, c],
                 Implies(And(r >= 0, r < rows - 1, c > 0, c < cols - 1),
                         Not(And(grid(r, c) == grid(r+1, c+1),
                                 grid(r, c) == grid(r+1, c),
                                 grid(r, c) == grid(r+1, c-1))))))
    # Bottom Left
    s.add(ForAll([r, c],
                 Implies(And(r >= 0, r < rows - 1, c > 0, c < cols),
                         Not(And(grid(r, c) == grid(r+1, c),
                                 grid(r, c) == grid(r+1, c-1),
                                 grid(r, c) == grid(r, c-1))))))
    # Left
    s.add(ForAll([r, c],
                 Implies(And(r > 0, r < rows - 1, c > 0, c < cols),
                         Not(And(grid(r, c) == grid(r+1, c-1),
                                 grid(r, c) == grid(r, c-1),
                                 grid(r, c) == grid(r-1, c-1))))))
    # Top Left
    s.add(ForAll([r, c],
                 Implies(And(r > 0, r < rows, c > 0, c < cols),
                         Not(And(grid(r, c) == grid(r, c-1),
                                 grid(r, c) == grid(r-1, c-1),
                                 grid(r, c) == grid(r-1, c))))))



    start_points = [a for couple in grid_start for a in couple]
    # The number of adjacent (non diagonal) of the same color is exactly 2 for
    # normal cells and exactly 1 for starting points
    for i in range(rows):
        for j in range(cols):
            if (i, j) in start_points:
                K = 1
            else:
                K = 2
            # 4 directions
            if i > 0 and i < rows - 1 and j > 0 and j < cols - 1:
                s.add(K ==
                      (If(grid(i, j) == grid(i-1, j), 1, 0)
                           + If(grid(i, j) == grid(i, j+1), 1, 0)
                           + If(grid(i, j) == grid(i+1, j), 1, 0)
                           + If(grid(i, j) == grid(i, j-1), 1, 0)))
            # 3 directions
            if i > 0 and i < rows - 1 and j == 0 and j < cols - 1:
                s.add(K ==
                      (If(grid(i, j) == grid(i-1, j), 1, 0)
                           + If(grid(i, j) == grid(i, j+1), 1, 0)
                           + If(grid(i, j) == grid(i+1, j), 1, 0)))
            # 3 directions
            if i == 0 and i < rows - 1 and j > 0 and j < cols - 1:
                s.add(K ==
                      (If(grid(i, j) == grid(i, j+1), 1, 0)
                           + If(grid(i, j) == grid(i+1, j), 1, 0)
                           + If(grid(i, j) == grid(i, j-1), 1, 0)))
            # 3 directions
            if i > 0 and i < rows - 1 and j > 0 and j == cols - 1:
                s.add(K ==
                      (If(grid(i, j) == grid(i+1, j), 1, 0)
                           + If(grid(i, j) == grid(i, j-1), 1, 0)
                           + If(grid(i, j) == grid(i-1, j), 1, 0)))
            # 3 directions
            if i > 0 and i == rows - 1 and j > 0 and j < cols - 1:
                s.add(K ==
                      (If(grid(i, j) == grid(i, j-1), 1, 0)
                           + If(grid(i, j) == grid(i-1, j), 1, 0)
                           + If(grid(i, j) == grid(i, j+1), 1, 0)))
            # 2 directions
            if i > 0 and i == rows - 1 and j == 0 and j < cols - 1:
                s.add(K ==
                      (If(grid(i, j) == grid(i-1, j), 1, 0)
                           + If(grid(i, j) == grid(i, j+1), 1, 0)))
            # 2 directions
            if i == 0 and i < rows - 1 and j == 0 and j < cols - 1:
                s.add(K ==
                      (If(grid(i, j) == grid(i, j+1), 1, 0)
                           + If(grid(i, j) == grid(i+1, j), 1, 0)))
            # 2 directions
            if i == 0 and i < rows - 1 and j > 0 and j == cols - 1:
                s.add(K ==
                      (If(grid(i, j) == grid(i+1, j), 1, 0)
                           + If(grid(i, j) == grid(i, j-1), 1, 0)))
            # 2 directions
            if i > 0 and i == rows - 1 and j > 0 and j == cols - 1:
                s.add(K ==
                      (If(grid(i, j) == grid(i, j-1), 1, 0)
                           + If(grid(i, j) == grid(i-1, j), 1, 0)))

    if s.check() == unsat:
        print()
        print("UNSAT")
        print(core)
        return None

    m = s.model()
    return [[m.evaluate(grid(i, j)).as_long() for j in range(size[1])] for i in range(size[0])]

def main():
    # TODO: Check Tetris configurations
    # TODO: Check for Loops

    sol = solve_sat(INPUT, LEVEL_SIZE)
    if not sol:
        print("Goddammit UNSAT!")
        return
    for i in range(len(sol)):
        print([sol[i][j] for j in range(len(sol[0]))])

if __name__ == '__main__':
    main()
