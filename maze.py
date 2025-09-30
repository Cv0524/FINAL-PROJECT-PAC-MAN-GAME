import tkinter as tk
import random

WIDTH = 600
HEIGHT = 600
CELL = 20  # cell size in pixels (600/20 = 30x30 grid)
ROWS = HEIGHT // CELL
COLS = WIDTH // CELL

# Each cell has walls: [top, right, bottom, left]
def init_maze(rows, cols):
    walls = [[[True, True, True, True] for _ in range(cols)] for _ in range(rows)]
    visited = [[False for _ in range(cols)] for _ in range(rows)]
    return walls, visited

def neighbors(r, c, rows, cols):
    nbs = []
    if r > 0: nbs.append((r-1, c, 0, 2))   # up:    current.top,    neighbor.bottom
    if c < cols-1: nbs.append((r, c+1, 1, 3)) # right: current.right,  neighbor.left
    if r < rows-1: nbs.append((r+1, c, 2, 0)) # down:  current.bottom, neighbor.top
    if c > 0: nbs.append((r, c-1, 3, 1))   # left:  current.left,   neighbor.right
    return nbs

def generate_maze(walls, visited, rows, cols, start=(0,0)):
    stack = [start]
    sr, sc = start
    visited[sr][sc] = True
    while stack:
        r, c = stack[-1]
        unvisited = [(nr, nc, cw, nw) for (nr, nc, cw, nw) in neighbors(r, c, rows, cols) if not visited[nr][nc]]
        if unvisited:
            nr, nc, cur_wall, nb_wall = random.choice(unvisited)
            # remove walls between current and neighbor
            walls[r][c][cur_wall] = False
            walls[nr][nc][nb_wall] = False
            visited[nr][nc] = True
            stack.append((nr, nc))
        else:
            stack.pop()

def draw_grid(canvas, width, height, cell, color="#dddddd"):
    # vertical lines
    for x in range(0, width + 1, cell):
        canvas.create_line(x, 0, x, height, fill=color)
    # horizontal lines
    for y in range(0, height + 1, cell):
        canvas.create_line(0, y, width, y, fill=color)

def draw_maze(canvas, walls, rows, cols, cell, wall_color="black", wall_width=2):
    for r in range(rows):
        for c in range(cols):
            x = c * cell
            y = r * cell
            top, right, bottom, left = walls[r][c]
            if top:
                canvas.create_line(x, y, x + cell, y, fill=wall_color, width=wall_width)
            if right:
                canvas.create_line(x + cell, y, x + cell, y + cell, fill=wall_color, width=wall_width)
            if bottom:
                canvas.create_line(x, y + cell, x + cell, y + cell, fill=wall_color, width=wall_width)
            if left:
                canvas.create_line(x, y, x, y + cell, fill=wall_color, width=wall_width)

def carve_entrances(walls, rows, cols):
    # open top wall of start and bottom wall of end for entry/exit
    walls[0][0][0] = False             # start top
    walls[rows-1][cols-1][2] = False   # end bottom

def main():
    root = tk.Tk()
    root.title("Tkinter Maze 600x600")

    canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white")
    canvas.pack()

    # background grid
    draw_grid(canvas, WIDTH, HEIGHT, CELL, color="#e5e5e5")

    # maze data
    walls, visited = init_maze(ROWS, COLS)
    generate_maze(walls, visited, ROWS, COLS, start=(0, 0))
    carve_entrances(walls, ROWS, COLS)

    # draw maze walls
    draw_maze(canvas, walls, ROWS, COLS, CELL, wall_color="black", wall_width=2)

    root.mainloop()

if __name__ == "__main__":
    main()
