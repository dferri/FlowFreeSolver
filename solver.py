#!/usr/bin/env python3
import copy

LEVEL_SIZE = (5, 5)
INPUT = [[(0, 0), (4, 1)], [(0, 2), (3, 1)], [(0, 4), (3, 3)], [(1, 2), (4, 2)], [(1, 4), (4, 3)]]

def print_grid(grid):
    for l in grid:
        print(" ".join(["{:3}".format(i) if i >= 0 else "   " for i in l]))

def find_first_undefined_cell(grid):
    """Returns the r,c of the first undefined cell"""
    for x,row in enumerate(grid):
        for y,vy in enumerate(row):
            if vy < 0:
                return x, y
    return -1, -1

def check_grid_pos(grid, r, c):
    return check_grid_val(grid, r, c, grid[r][c])

def check_grid_val(grid, r, c, v):
    """Return the possible values for a cell in the r,c position"""
    n = max([max(l) for l in grid])
    h = len(grid)
    w = len(grid[0])

    # Avoid 4 adjacent cells of of same color
    nope = []
    # Left
    if r > 0 and r < h - 1 and c > 0:
        if (grid[r+1][c-1] == v
            and v == grid[r][c-1]
            and v == grid[r-1][c-1]):
            return False
    # Top Left
    if r > 0 and c > 0:
        if (grid[r-1][c] == v
            and v == grid[r-1][c-1]
            and v == grid[r][c-1]):
            return False
    # Top
    if r > 0 and c > 0 and c < w - 1:
        if (grid[r-1][c-1] == v
            and v == grid[r-1][c]
            and v == grid[r-1][c+1]):
            return False

    # Top Right
    if r > 0 and c < w - 1:
        if (grid[r][ c+1] == v
            and v == grid[r-1][ c+1]
            and v == grid[r-1][c]):
            return False
    # Right
    if r > 0 and r < h - 1 and c < w - 1:
        if (grid[r-1][c+1] == v
            and v == grid[r][c+1]
            and v == grid[r+1][c+1]):
            return False
    # Bottom Right
    if r < h - 1 and c < w - 1:
        if (grid[r][c+1] == v
            and v == grid[r+1][c+1]
            and v == grid[r+1][c]):
            return False
    # Bottom
    if r < h - 1 and c > 0 and c < w - 1:
        if (grid[r+1][c+1] == v
            and v == grid[r+1][c]
            and v == grid[r+1][c-1]):
            return False
    # Bottom Left
    if r > 0 and r < h - 1 and c > 0 and c < w - 1:
        if (grid[r+1][c] == v
            and v == grid[r+1][c-1]
            and v == grid[r-1][c-1]):
            return False

    # Tetris Left
    if r > 0 and r < h - 1 and c > 0:
        if (grid[r+1][c] == v
            and v == grid[r][c-1]
            and v == grid[r-1][c]):
            return False
    # Tetris Top
    if r > 0 and c > 0 and c < w - 1:
        if (grid[r][c-1] == v
            and v == grid[r-1][c]
            and v == grid[r][c+1]):
            return False
    # Tetris Right
    if r > 0 and r  < h - 1 and c < w - 1:
        if (grid[r-1][c] == v
            and v == grid[r][c+1]
            and v == grid[r+1][c]):
            return False
    # Tetris Bottom
    if r < h - 1 and c > 0 and c < w - 1:
        if (grid[r][c+1] == v
            and v == grid[r+1][c]
            and v == grid[r][c-1]):
            return False

    return True


def snake_can_reach(grid, v, start, end, grid_start, debug=False):
    """Returns True if snake of color `v` can go from `start` to `end`"""
    r,c = start
    n = max([max(l) for l in grid])
    h = len(grid)
    w = len(grid[0])
    # debug = True
    if debug:
        print("snake_can_reach")
        print(grid_start[v][1][0], grid_start[v][1][1])
        print("start: ", start)
        print("end: ", end)
        print("r, c: ", r, c)
        print("v: ", v)
        print(15)
        print_grid(grid)
        print(2)

    # We're done!
    if start == end:
        return True
    # We're also done!
    for tr, tc in [(r, c-1), (r-1, c), (r, c+1), (r+1, c)]:
        if (tr >= 0 and tr < h and tc >= 0 and tc < w):
            if (tr, tc) == end:
                return True


    for tr, tc in [(r, c-1), (r-1, c), (r, c+1), (r+1, c)]:
        if check_grid_snake_val(grid, grid_start, tr, tc, v, ignore_reach=False):
            grid1 = copy.deepcopy(grid)
            grid1[tr][tc] = v
            # print("grid1")
            # print_grid(grid1)
            res = snake_can_reach(grid1, v,
                                  (tr, tc),
                                  end,
                                  grid_start)
            if res:
                return True
    return False


def check_grid_snake_val(grid, grid_start, r, c, v, ignore_reach=True):
    """Count the occurences of `v` in the cells adjacent to r,c (not
    diagonally tho)"""
    n = max([max(l) for l in grid])
    h = len(grid)
    w = len(grid[0])
    count = 0

    # We're actually INSIDE the grid
    if not (r >= 0 and r < h and c >= 0 and c < w):
        return False

    # End of this color
    if (grid[r][c] == v
        and (r, c) == grid_start[v][1]):

        # Shouldn't cut off other colors:
        if ignore_reach:
            # print("grid:")
            # print_grid(grid)
            # print("current: ", v)
            for i in range(n+1):
                if i <= v:
                    continue
                res = snake_can_reach(grid,
                                    i,
                                    grid_start[i][0],
                                    grid_start[i][1],
                                    grid_start)
                if not res:
                    print("cant reach :", i)
                    return False
                print("can reach :", i)
        return True

    # This cell is already defined
    if (grid[r][c] >= 0):
        return False

    # Shouldn't cut off other colors:
    # if ignore_reach:
    #     print("grid:")
    #     print_grid(grid)
    #     print("current: ", v)
    #     for i in range(n+1):
    #         if i <= v:
    #             continue
    #         res = snake_can_reach(grid,
    #                               i,
    #                               grid_start[i][0],
    #                               grid_start[i][1],
    #                               grid_start)
    #         if not res:
    #             print("cant reach :", i)
    #             return False
    #         print("can reach :", i)


    # We're snaking, so the number of adjacent cells of same color must be
    # exactly one
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            if r + dx < 0 or r + dx >= w:
                continue
            if c + dy < 0 or c + dy >= h:
                continue
            if dx == 0 or dy == 0:
                if (r + dx, c + dy) != grid_start[v][1]:
                    if grid[r + dx][c + dy] == v:
                        count += 1
    return count == 1

def check_grid_snake_val1(grid, r, c, v):
    """Return the possible values for a cell in the r,c position,
    keeping in mind to not connect the same color to itself"""
    if not check_grid_val(grid, r, c, v):
        return False

    n = max([max(l) for l in grid])
    h = len(grid)
    w = len(grid[0])
    # Horizontal
    if c > 0 and c < w - 1:
        if (grid[r][c+1] == v
            and v == grid[r][c]
            and v == grid[r][c-1]):
            return False
    # Vertical
    if r > 0 and r < h - 1:
        if (grid[r+1][c] == v
            and v == grid[r][c]
            and v == grid[r-1][c]):
            return False
    return True

def rekt_count(grid, r, c):
    n = max([max(l) for l in grid])
    h = len(grid)
    w = len(grid[0])
    v = grid[r][c]
    count = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            if r + dx < 0 or r + dx >= w:
                continue
            if c + dy < 0 or c + dy >= h:
                continue
            if dx == 0 or dy == 0:
                if grid[r + dx][c + dy] == v:
                    count += 1
    return count

def check_grid(grid, grid_start):
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if not check_grid_pos(grid, r, c):
                return False
    # Special check for start points
    for s in grid_start:
        if rekt_count(grid, s[0][0], s[0][1]) != 1:
            return False
        if rekt_count(grid, s[1][0], s[1][1]) != 1:
            return False
    return True


def possible_values(grid, r, c):
    res = []
    n = max([max(l) for l in grid])
    for i in range(n+1):
        if check_grid_val(grid, r, c, i):
            res.append(i)
    return res

def possible_values1(grid, r, c):
    """Return the possible values for a cell in the r,c position"""
    n = max([max(l) for l in grid])
    h = len(grid)
    w = len(grid[0])

    # ret = []
    # count = [0 for i in range(n+1)]
    # for dx in [-1, 0, 1]:
    #     for dy in [-1, 0, 1]:
    #         if dx == 0 and dy == 0:
    #             continue
    #         if r + dx < 0 or r + dx >= w:
    #             continue
    #         if c + dy < 0 or c + dy >= h:
    #             continue
    #         if grid[r + dx][c + dy] >= 0:
    #             count[grid[r + dx][c + dy]] += 1
    # Avoid 4 adjacent cells of of same color
    nope = []
    # Left
    if r > 0 and r < h - 1 and c > 0:
        if (grid[r+1][c-1] == grid[r][c-1]
            and grid[r][c-1] == grid[r-1][c-1]):
            nope.append(grid[r-1][c-1])
    # Top Left
    if r > 0 and c > 0:
        if (grid[r-1][c] == grid[r-1][c-1]
            and grid[r-1][c-1] == grid[r][c-1]):
            nope.append(grid[r-1][c-1])
    # Top
    if r > 0 and c > 0 and c < w - 1:
        if (grid[r-1][c-1] == grid[r-1][c]
            and grid[r-1][c] == grid[r-1][c+1]):
            nope.append(grid[r-1][c+1])

    # Top Right
    if r > 0 and c < w - 1:
        if (grid[r][ c+1] == grid[r-1][ c+1]
            and grid[r-1][c+1] == grid[r-1][c]):
            nope.append(grid[r-1][c])
    # Right
    if r > 0 and r < h - 1 and c < w - 1:
        if (grid[r-1][c+1] == grid[r][c+1]
            and grid[r][c+1] == grid[r+1][c+1]):
            nope.append(grid[r+1][c+1])
    # Bottom Right
    if r < h - 1 and c < w - 1:
        if (grid[r][c+1] == grid[r+1][c+1]
            and grid[r+1][c+1] == grid[r+1][c]):
            nope.append(grid[r+1][c])
    # Bottom
    if r < h - 1 and c > 0 and c < w - 1:
        if (grid[r+1][c+1] == grid[r+1][c]
            and grid[r+1][c] == grid[r+1][c-1]):
            nope.append(grid[r+1][c-1])
    # Bottom Left
    if r > 0 and r < h - 1 and c > 0 and c < w - 1:
        if (grid[r+1][c] == grid[r+1][c-1]
            and grid[r+1][c-1] == grid[r-1][c-1]):
            nope.append(grid[r-1][c-1])

    # Tetris Left
    if r > 0 and r < h - 1 and c > 0:
        if (grid[r+1][c] == grid[r][c-1]
            and grid[r][c-1] == grid[r-1][c]):
            nope.append(grid[r-1][c])

    # Tetris Top
    if r > 0 and c > 0 and c < w - 1:
        if (grid[r][c-1] == grid[r-1][c]
            and grid[r-1][c] == grid[r][c+1]):
            nope.append(grid[r+1][c+1])

    # Tetris Right
    if r > 0 and r  < h - 1 and c < w - 1:
        if (grid[r-1][c] == grid[r][c+1]
            and grid[r][c+1] == grid[r+1][c]):
            nope.append(grid[r+1][c])

    # Tetris Bottom
    if r < h - 1 and c > 0 and c < w - 1:
        if (grid[r][c+1] == grid[r+1][c]
            and grid[r+1][c] == grid[r][c-1]):
            nope.append(grid[r][c-1])

    # Check the fucking tetris pieces
    # for i in range(n+1):

    #     if 
    #     x1 = max(r - 1, 0)
    #     y1 = max(c - 1, 0)
    #     x2 = min(r + 1, w)
    #     y2 = min(c + 1, h)

    # for c in count:
    #     if c > 1:
    # print("count")
    # print(count)
    return [i for i in range(n+1) if i not in nope]



def iter_solve(grid, grid_start):
    """Recursively guess and search for the solution"""
    r, c = find_first_undefined_cell(grid)
    if r == -1 or c == -1:
        if check_grid(grid, grid_start):
            return grid
        return None

    pos = possible_values(grid, r, c)
    if not pos:
        return None
    for p in pos:
        grid1 = copy.deepcopy(grid)
        grid1[r][c] = p
        res = iter_solve(grid1, grid_start)
        if res is not None:
            return res
    return None

def iter_snake_solve(grid, grid_start, cur, r, c, debug=False):
    # debug = True
    if debug:
        print("wowde")
        print(grid_start[cur][1][0], grid_start[cur][1][1])
        print("r, c: ", r, c)
        print("cur: ", cur)
        print(18)
        print_grid(grid)
        print(2)
    n = max([max(l) for l in grid])
    h = len(grid)
    w = len(grid[0])

    if (r == grid_start[cur][1][0]
        and c == grid_start[cur][1][1]):
        if cur == n:
            # We're done!
            return grid
        return iter_snake_solve(grid, grid_start, cur+1, grid_start[cur+1][0][0],
                                grid_start[cur+1][0][1])

    print("Advancing! cur: ", cur)
    print("grid adv")
    print_grid(grid)
    # Left
    if c > 0:
        tr = r
        tc = c-1
        # Next cell is undefined or the end for this color
        if check_grid_snake_val(grid, grid_start, tr, tc, cur):
            grid1 = copy.deepcopy(grid)
            grid1[tr][tc] = cur
            print("grid1")
            print_grid(grid1)
            res = iter_snake_solve(grid1, grid_start,
                                   cur, tr, tc)
            if res is not None:
                return res
    # Top
    if r > 0:
        tr = r-1
        tc = c
        if check_grid_snake_val(grid, grid_start, tr, tc, cur):
            grid1 = copy.deepcopy(grid)
            grid1[tr][tc] = cur
            res = iter_snake_solve(grid1, grid_start,
                                   cur, tr, tc)
            if res is not None:
                return res
    # Right
    if c < w - 1:
        tr = r
        tc = c+1
        if check_grid_snake_val(grid, grid_start, tr, tc, cur):
            grid1 = copy.deepcopy(grid)
            grid1[tr][tc] = cur
            res = iter_snake_solve(grid1, grid_start,
                                   cur, tr, tc)
            if res is not None:
                return res
    # Bottom
    if r < h - 1:
        tr = r+1
        tc = c
        if check_grid_snake_val(grid, grid_start, tr, tc, cur):
            grid1 = copy.deepcopy(grid)
            grid1[tr][tc] = cur
            res = iter_snake_solve(grid1, grid_start,
                                   cur, tr, tc)
            if res is not None:
                return res
    return None



def solve(grid_start, size):
    # return [[0, 1, 1, 2, 2], [0, 1, 3, 2, 4], [0, 1, 3, 2, 4], [0, 1, 3, 2, 4], [0, 0, 3, 4, 4]]
    tmp = [[-1 for j in range(size[0])] for i in range(size[0])]
    for i,((x1, y1), (x2, y2)) in enumerate(grid_start):
        tmp[x1][y1] = i
        tmp[x2][y2] = i
    return iter_snake_solve(tmp, grid_start, 0, grid_start[0][0][0], grid_start[0][0][1])

def main():
    # print(iter_solve([[0, -1, 1, -1, 2], [0, 1, 3, 2, 4], [0, 1, 3, 2, 4], [0, 1, 3, 2, 4], [0, 0, 3, 4, 4]], [[(0, 0), (4, 1)], [(0, 2), (3, 1)], [(0, 4), (3, 3)], [(1, 2), (4, 2)], [(1, 4), (4, 3)]]))
    # if check_grid([[0, 1, 1, 2, 2], [0, 1, 3, 2, 4], [0, 1, 3, 2, 4], [0, 1, 3, 2, 4], [0, 0, 3, 4, 4]], [[(0, 0), (4, 1)], [(0, 2), (3, 1)], [(0, 4), (3, 3)], [(1, 2), (4, 2)], [(1, 4), (4, 3)]]):
    #     print("yes")
    # else:
    #     print("nope")
    print(solve(INPUT, LEVEL_SIZE))

if __name__ == '__main__':
    main()
