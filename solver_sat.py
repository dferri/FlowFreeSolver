#!/usr/bin/env python3

import copy
import sys
from z3 import *

# Initialize z3
z3.init("/usr/lib/python3.6/site-packages/z3")

def print_grid(grid):
    for l in grid:
        print(" ".join(["{:3}".format(i) if i >= 0 else "   " for i in l]))

def solve_sat(grid_start, size, debug=False):
    """Solves the puzzle using Z3"""
    r, c = Ints("r c")
    rows, cols = size
    n = len(grid_start)
    # This is the function that represents the grid
    # grid[x, y] == k means the cell at (x, y) is of color k
    grid = Function("grid", IntSort(), IntSort(), IntSort())
    # This function gives Z3 the knowledge of direction of the flows
    # flow[x, y] == k means the cell at (x, y) is k-th cell of its flow
    # e.g. flow[x, y] == 0 for every (x, y) starting point of a flow
    flow = Function("flow", IntSort(), IntSort(), IntSort())
    s = Solver()

    start_points = [a for couple in grid_start for a in couple]
    dx1, dy1, dx2, dy2, dx3, dy3, dx4, dy4 = Ints(
        "dx1, dy1, dx2, dy2, dx3, dy3, dx4, dy4")

    ### Grid constraints
    # Defined only inside the grid and values in the right range
    s.add(ForAll([r, c], Implies(And(r >= 0, r < rows,
                                     c >= 0, c < cols),
                                 And(grid(r, c) >= 0,
                                     grid(r, c) < n))))
    s.add(ForAll([r, c], Implies(Or(r < 0, r >= size[0],
                                    c < 0, c >= size[1]),
                                 grid(r, c) == -1)))
    # Set the initial conditions
    for i, ((x1, y1), (x2, y2)) in enumerate(grid_start):
        s.add(grid(x1, y1) == i)
        s.add(grid(x2, y2) == i)
    # Other constraints
    # There must not be any squares of the same color
    # Square
    s.assert_and_track(
        ForAll([r, c],
               Implies(And(r >= 0, r < rows - 1, c >= 0, c < cols - 1),
                       Not(And(grid(r, c) == grid(r  , c+1),
                               grid(r, c) == grid(r+1, c+1),
                               grid(r, c) == grid(r+1, c  ))))),
        "Square")

    # The number of adjacent (non diagonal) of the same color is exactly 2 for
    # normal cells and exactly 1 for starting points
    for i in range(rows):
        for j in range(cols):
            if (i, j) in start_points:
                K = 1
            else:
                K = 2
            # 4 directions 4_0
            if i > 0 and i < rows - 1 and j > 0 and j < cols - 1:
                s.assert_and_track(
                    K ==
                      (  If(grid(i, j) == grid(i-1, j  ), 1, 0)
                       + If(grid(i, j) == grid(i  , j+1), 1, 0)
                       + If(grid(i, j) == grid(i+1, j  ), 1, 0)
                       + If(grid(i, j) == grid(i  , j-1), 1, 0)),
                    "dir_4_0_K_{}_i_j_{}_{}".format(K, i, j))
            # 3 directions 3_1
            if i > 0 and i < rows - 1 and j == 0 and j < cols - 1:
                s.assert_and_track(
                    K ==
                      (  If(grid(i, j) == grid(i-1, j  ), 1, 0)
                       + If(grid(i, j) == grid(i  , j+1), 1, 0)
                       + If(grid(i, j) == grid(i+1, j  ), 1, 0)),
                    "dir_3_1_K_{}_i_j_{}_{}".format(K, i, j))
            # 3 directions 3_2
            if i == 0 and i < rows - 1 and j > 0 and j < cols - 1:
                s.assert_and_track(
                    K ==
                      (  If(grid(i, j) == grid(i  , j+1), 1, 0)
                       + If(grid(i, j) == grid(i+1, j  ), 1, 0)
                       + If(grid(i, j) == grid(i  , j-1), 1, 0)),
                    "dir_3_2_K_{}_i_j_{}_{}".format(K, i, j))
            # 3 directions 3_3
            if i > 0 and i < rows - 1 and j > 0 and j == cols - 1:
                s.assert_and_track(
                    K ==
                      (  If(grid(i, j) == grid(i+1, j  ), 1, 0)
                       + If(grid(i, j) == grid(i  , j-1), 1, 0)
                       + If(grid(i, j) == grid(i-1, j  ), 1, 0)),
                    "dir_3_3_K_{}_i_j_{}_{}".format(K, i, j))
            # 3 directions 3_4
            if i > 0 and i == rows - 1 and j > 0 and j < cols - 1:
                s.assert_and_track(
                    K ==
                      (  If(grid(i, j) == grid(i  , j-1), 1, 0)
                       + If(grid(i, j) == grid(i-1, j  ), 1, 0)
                       + If(grid(i, j) == grid(i  , j+1), 1, 0)),
                    "dir_3_4_K_{}_i_j_{}_{}".format(K, i, j))
            # 2 directions 2_5
            if i > 0 and i == rows - 1 and j == 0 and j < cols - 1:
                s.assert_and_track(
                    K ==
                      (  If(grid(i, j) == grid(i-1, j  ), 1, 0)
                       + If(grid(i, j) == grid(i  , j+1), 1, 0)),
                    "dir_2_5_K_{}_i_j_{}_{}".format(K, i, j))
            # 2 directions 2_6
            if i == 0 and i < rows - 1 and j == 0 and j < cols - 1:
                s.assert_and_track(
                    K ==
                      (  If(grid(i, j) == grid(i  , j+1), 1, 0)
                       + If(grid(i, j) == grid(i+1, j  ), 1, 0)),
                    "dir_2_6_K_{}_i_j_{}_{}".format(K, i, j))
            # 2 directions 2_7
            if i == 0 and i < rows - 1 and j > 0 and j == cols - 1:
                s.assert_and_track(
                    K ==
                      (  If(grid(i, j) == grid(i+1, j  ), 1, 0)
                       + If(grid(i, j) == grid(i  , j-1), 1, 0)),
                    "dir_2_7_K_{}_i_j_{}_{}".format(K, i, j))
            # 2 directions 2_8
            if i > 0 and i == rows - 1 and j > 0 and j == cols - 1:
                s.assert_and_track(
                    K ==
                      (  If(grid(i, j) == grid(i  , j-1), 1, 0)
                       + If(grid(i, j) == grid(i-1, j  ), 1, 0)),
                "dir_2_8_K_{}_i_j_{}_{}".format(K, i, j))


    ### Flow constraints
    # Defined only inside the grid and >= 0 values
    s.add(ForAll([r, c], Implies(And(r >= 0, r < rows,
                                     c >= 0, c < cols),
                                 flow(r, c) >= 0)))
    s.add(ForAll([r, c], Implies(Or(r < 0, r >= rows,
                                    c < 0, c >= cols),
                                 flow(r, c) == -1)))

    # Set the initial conditions
    for i, ((x1, y1), (x2, y2)) in enumerate(grid_start):
        s.add(flow(x1, y1) == 0)

    # For every cell that is not a starting point there must be two adjacent
    # non diagonal cells with decreasing and increasing value respectively
    for i in range(rows):
        for j in range(cols):
            if (i, j) in start_points:
                s.assert_and_track(
                    Exists(
                        [dx1, dy1],
                        And(# Adjacent orthogonal cell
                            Or((dx1 == 1), (dx1 == 0), (dx1 == -1)),
                            Or((dy1 == 1), (dy1 == 0), (dy1 == -1)),

                            Or(Not(dx1 == 0), Not(dy1 == 0)),
                            # Inside the grid
                            And((i + dx1) >= 0, (i + dx1) < rows,
                                (j + dy1) >= 0, (j + dy1) < cols),
                            # Of the same color
                            grid(i, j) == grid(i + dx1, j + dy1),

                            Or(flow(i, j) == (flow(i + dx1, j + dy1) + 1),
                               flow(i, j) == (flow(i + dx1, j + dy1) - 1))
                        )
                    ), "flow_starting_i_j_{}_{}".format(i, j))
            else:
                s.assert_and_track(
                    Exists(
                        [dx1, dy1, dx2, dy2],
                        And(# Different adjacent orthogonal cells
                            Or(And(dx1 == -1, dy1 == 0), And(dx1 == 0, dy1 ==  1),
                               And(dx1 ==  1, dy1 == 0), And(dx1 == 0, dy1 == -1)),
                            Or(And(dx2 == -1, dy2 == 0), And(dx2 == 0, dy2 ==  1),
                               And(dx2 ==  1, dy2 == 0), And(dx2 == 0, dy2 == -1)),

                            Or(Not(dx1 == dx2), Not(dy1 == dy2)),
                            # Inside the grid
                            And((i + dx1) >= 0, (i + dx1) < rows,
                                (j + dy1) >= 0, (j + dy1) < cols),
                            And((i + dx2) >= 0, (i + dx2) < rows,
                                (j + dy2) >= 0, (j + dy2) < cols),
                            # Of the same color
                            grid(i + dx1, j + dy1) == grid(i, j),
                            grid(i + dx2, j + dy2) == grid(i, j),

                            flow(i, j) == (flow(i + dx1, j + dy1) + 1),
                            flow(i + dx2, j + dy2) == (flow(i, j) + 1)
                        )
                    ), "flow_normal_i_j_{}_{}".format(i, j))

    if s.check() == unsat:
        if debug:
            print()
            print("UNSAT")
            for e in s.unsat_core():
                print(e)
            return None, None
        return None

    m = s.model()
    if debug:
        return ([[m.evaluate(grid(i, j)).as_long() for j in range(size[1])]
                 for i in range(size[0])],
                [[m.evaluate(flow(i, j)).as_long() for j in range(size[1])]
                 for i in range(size[0])])
    else:
        return [[m.evaluate(grid(i, j)).as_long() for j in range(size[1])]
                for i in range(size[0])]

def main():
    LEVEL_SIZE = (5, 5)
    INPUT = [[(0, 0), (4, 1)], [(0, 2), (3, 1)], [(0, 4), (3, 3)], [(1, 2), (4, 2)], [(1, 4), (4, 3)]]
    sol = solve_sat(INPUT, LEVEL_SIZE)
    if not sol:
        print("UNSAT!")
        sys.exit(1)
    for i in range(len(sol)):
        print([sol[i][j] for j in range(len(sol[0]))])

if __name__ == '__main__':
    main()
