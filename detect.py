#!/usr/bin/env python3

import argparse
import sys

import cv2
import numpy as np

import solver
import solver_sat

minLineLength = 1000
maxLineGap = 10
EPS = 10
COLOR_EPS = 60

def show_img(img, width=400, height=800):
    """Display the image in a window of `width`x`height` (default 400x800)
    and save at full resolution in /tmp/flow_tmp.png"""
    cv2.imwrite("/tmp/flow_tmp.png", img)

    img = cv2.resize(img, (width, height))
    while True:
        cv2.imshow("wow", img)
        k = cv2.waitKey(0)
        if k == 27 or k == 113:    # wait for ESC or 'q' key to exit
            cv2.destroyAllWindows()
            break


def dist (x1, y1, x2, y2):
    return (y2 - y1)*(y2 - y1) + (x2 - x1)*(x2 - x1)

def find_intersections(lines):
    """Returns a list of the intersections of the lines in the list `lines`
    A line is described by the list [x1, y1, x2, y2], i.e. the line from
    (x1, y1) to (x2, y2)"""
    intersections = []
    # Convert lines to the form Ax + By = C
    # and use Cramer to find intersections
    l = []
    for line in lines:
        x1, y1, x2, y2 = line
        l.append([x2 - x1,
                  y1 - y2,
                  (x2 - x1)*y1 - (y2 - y1)*x1])

    for a1, b1, c1 in l:
        for a2, b2, c2 in l:
            det = a1*b2 - a2*b1

            if det != 0:
                ix = (b2*c1 - b1*c2)/det
                iy = (a1*c2 - a2*c1)/det

                # Add intersection only if distant enough from other intersections
                dang = True
                for x,y in intersections:
                    if dist(x, y, ix, iy) < 5*EPS:
                        dang = False
                        break
                if dang:
                    intersections.append([ix, iy])
    return intersections


def find_grid_coord(intersections):
    """Find the coordinates of the intersections"""
    # Find the x and y of the grid:
    xs = []
    ys = []
    for x,y in intersections:
        dangX = True
        dangY = True
        for t in xs:
            if abs(t - x) < EPS:
                dangX = False

        for t in ys:
            if abs(t - y) < EPS:
                dangY = False

        if dangX:
            xs.append(int(x))
        if dangY:
            ys.append(int(y))

    xs.sort()
    ys.sort()
    return xs, ys

def find_colors(img, gray, xs, ys):
    colors = []
    for r in range(len(xs) - 1):
        row = []
        for c in range(len(ys) - 1):
            x1 = xs[r]
            x2 = xs[r+1]
            y1 = ys[c]
            y2 = ys[c+1]

            # Mask for the cell we're analyzing
            rect_mask = np.zeros(img.shape[:2], np.uint8)
            rect_mask[x1:x2, y1:y2] = 255

            circles = cv2.HoughCircles(gray[x1:x2, y1:y2], cv2.HOUGH_GRADIENT,
                                    1, 20, param1=50, param2=30,
                                    minRadius=20, maxRadius=0)

            # We must find exactly one circle
            if circles is None:
                continue
            if len(circles) != 1:
                continue

            circle_mask = np.zeros(img.shape[:2], np.uint8)
            circle = circles[0, 0]
            cv2.circle(circle_mask, (circle[0],circle[1]),
                    radius=int(circle[2] - 10),
                    color=(255,255,255), thickness=cv2.FILLED)
            col = cv2.mean(img, circle_mask)

            w, h = img.shape[:2]
            cx1 = max(int((x1 + x2)/2 - 10), 0)
            cy1 = max(int((y1 + y2)/2 - 10), 0)
            cx2 = min(int((x1 + x2)/2 + 10), w)
            cy2 = min(int((y1 + y2)/2 + 10), h)
            col = cv2.mean(img[cx1:cx2, cy1:cy2])
            colors.append((col, (r, c)))
    ret = {}
    for ((r, g, b, a), (x, y)) in colors:
        for (r1, g1, b1) in ret.keys():
            if (abs(r1 - r)
                + abs(g1 - g)
                + abs(b1 - b)) < COLOR_EPS:
                r = r1
                g = g1
                b = b1
                break
        ret.setdefault((r, g, b), []).append((x, y))
    return ret



def main():
    parser = argparse.ArgumentParser(
        description="Detect a FlowFree grid from a screenshot and solves it ")
    parser.add_argument("--no-solve",
                        action="store_true",
                        help="Just print the grid, do not solve it")
    parser.add_argument("img_path",
                        help="Path to the screenshot")
    args = parser.parse_args()

    img = cv2.imread(args.img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 100, apertureSize = 3)

    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100,
                            minLineLength=minLineLength, maxLineGap=maxLineGap)
    # Reformat the lines list
    lines = [line[0] for line in lines]

    # Find the intersections of all the lines
    intersections = find_intersections(lines)
    # Find the x and y of all the lines of the grid
    # NB maybe we could directly do this from the lines, without intersections
    xs, ys = find_grid_coord(intersections)

    colors = find_colors(img, gray, xs, ys)
    i = 0
    for k,v in colors.items():
        i += 1
    level_size = (len(xs) - 1, len(ys) - 1)
    color_map = []
    level_init = []
    for k,v in colors.items():
        color_map.append(k)
        level_init.append(v)
        if len(v) != 2:
            print("Failed to detect a proper grid!")
            print("Grid start:")
            for l in level_init:
                print(l)
            sys.exit(1)

    print(level_size)
    print(level_init)
    if args.no_solve:
        sys.exit(0)

    # Actually solve the puzzle
    # solution = solver.solve(level_init, level_size)
    solution = solver_sat.solve_sat(level_init, level_size)
    print()
    print(solution)

    start_points = [a for couple in level_init for a in couple]
    # Display solution
    for r in range(len(xs) - 1):
        for c in range(len(ys) - 1):
            hp = 30
            cx1 = int((xs[r] + xs[r + 1])/2 - hp)
            cy1 = int((ys[c] + ys[c + 1])/2 - hp)
            cx2 = int((xs[r] + xs[r + 1])/2 + hp)
            cy2 = int((ys[c] + ys[c + 1])/2 + hp)
            if (r, c) in start_points:
                continue
            cv2.rectangle(img, (cy1, cx1), (cy2, cx2),
                          color=color_map[solution[r][c]],
                          thickness=cv2.FILLED)
    show_img(img)

if __name__ == '__main__':
    main()
