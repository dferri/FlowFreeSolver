#!/usr/bin/env python3
l = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
ll = [[l[i], l[(i+1)%len(l)], l[(i+2)%len(l)]] for i in range(len(l))]
# i.e.
# [(-1, -1), (-1, 0), (-1, 1)]
# [(-1, 0), (-1, 1), (0, 1)]
# [(-1, 1), (0, 1), (1, 1)]
# [(0, 1), (1, 1), (1, 0)]
# [(1, 1), (1, 0), (1, -1)]
# [(1, 0), (1, -1), (0, -1)]
# [(1, -1), (0, -1), (-1, -1)]
# [(0, -1), (-1, -1), (-1, 0)]
# Top
# Top Right
# Right
# Bottom Right
# Bottom
# Bottom Left
# Left
# Top Left

names = [
    "Top",
    "Top Right",
    "Right",
    "Bottom Right",
    "Bottom",
    "Bottom Left",
    "Left",
    "Top Left"]

print()
s = ["-1", "  ", "+1"]

rc_constraints = []
grid_constraints = []
for index, ((x1, y1), (x2, y2), (x3, y3)) in enumerate(ll):
    rc_constraints = []
    if min(x1, x2, x3) < 0:
        rc_constraints.append("r > 0")
    else:
        rc_constraints.append("r >= 0")
    if max(x1, x2, x3) > 0:
        rc_constraints.append("r < rows - 1")
    else:
        rc_constraints.append("r < rows")
    if min(y1, y2, y3) < 0:
        rc_constraints.append("c > 0")
    else:
        rc_constraints.append("c >= 0")
    if max(y1, y2, y3) > 0:
        rc_constraints.append("c < cols - 1")
    else:
        rc_constraints.append("c < cols")
    rc_constraints_str = ", ".join(rc_constraints)

    grid_constraints = [
        "grid(r, c) == grid(r{}, c{})".format(s[x1+1], s[y1+1]),
        "grid(r{}, c{})".format(s[x2+1], s[y2+1]),
        "grid(r{}, c{})".format(s[x3+1], s[y3+1])]
    # Left
    # s.assert_and_track(
    #     ForAll([r, c],
    #            Implies(And(r > 0, r < h - 1, c > 0, c < w - 1),
    #                    Not(And(grid(r, c) == grid(r+1, c-1),
    #                            grid(r, c) == grid(r  , c-1),
    #                            grid(r, c) == grid(r-1, c-1))))),
    #     "left")
    print("    # " + names[index])
    print("    s.assert_and_track(")
    print("        ForAll([r, c],")
    print("               Implies(And(" + ", ".join(rc_constraints) + "),")
    print("                       Not(And("
          + ",\n                               grid(r, c) == ".join(grid_constraints)
          + ")))),")
    print("        \"" + names[index] + "\")")
    # print(rc_constraints)
    # print(grid_constraints)


directions_4 = [[(-1, 0), (0, 1), (1, 0), (0, -1)]]
directions_3 = [[(-1, 0), (0, 1), (1, 0)], [(0, 1), (1, 0), (0, -1)], [(1, 0), (0, -1), (-1, 0)], [(0, -1), (-1, 0), (0, 1)]]
directions_2 = [[(-1, 0), (0, 1)], [(0, 1), (1, 0)], [(1, 0), (0, -1)], [(0, -1), (-1, 0)]]

directions = directions_4 + directions_3 + directions_2

for number, dir in enumerate(directions):
    if_constraints = []
    print("            # {} directions {}_{}".format(len(dir), len(dir), number))
    minX = min([x for x,y in dir])
    if minX < 0:
        if_constraints.append("i > 0")
    else:
        if_constraints.append("i == 0")
    maxX = max(x for x,y in dir)
    if maxX > 0:
        if_constraints.append("i < rows - 1")
    else:
        if_constraints.append("i == rows - 1")
    minY = min(y for x,y in dir)
    if minY < 0:
        if_constraints.append("j > 0")
    else:
        if_constraints.append("j == 0")
    maxY = max(y for x,y in dir)
    if maxY > 0:
        if_constraints.append("j < cols - 1")
    else:
        if_constraints.append("j == cols - 1")
    addendums = []
    for dx, dy in dir:
        addendums.append("If(grid(i, j) == grid(i{}, j{}), 1, 0)"
                         .format(s[dx+1], s[dy+1]))
    # s.assert_and_track(
    #     ForAll([r, c],
    #            Implies(And(r > 0, r < rows, c > 0, c < cols),
    #                    (K ==
    #                      ( If(grid(r, c) == grid(r, c-1), 1, 0)
    #                      + If(grid(r, c) == grid(r, c-1), 1, 0))))))
    # print("    s.add(ForAll([r, c],")
    # print("                 Implies(And(" + ", ".join(if_constraints) + "),")
    # print("                         (K ==")
    # print("                          ("
    #       + "\n                           + ".join(addendums) + ")))))")
    # for i in range(rows):
    #     for j in range(cols):
    #         if (i, j) in start_points:
    #             K = 1
    #         else:
    #             K = 2
    #         # Bottom tetris
            # if i == 0 and i < rows and j > 0 and j < cols - 1:
            #     s.assert_and_track(
            #         K ==
            #           (  If(grid(i, j) == grid(i  , j+1), 1, 0)
            #            + If(grid(i, j) == grid(i+1, j  ), 1, 0)
            #            + If(grid(i, j) == grid(i  , j-1), 1, 0)),
            #         "count_K_i_j_{}_{}_{}".format(K, i, j))
    # 3 directions

    print("            if " + " and ".join(if_constraints) + ":")
    print("                s.assert_and_track(")
    print("                    K ==")
    print("                      (  "
          + "\n                       + ".join(addendums) + "),")
    print("                    \"dir_" + str(len(dir)) + "_" + str(number)
          + "_K_{}_i_j_{}_{}\".format(K, i, j))")
