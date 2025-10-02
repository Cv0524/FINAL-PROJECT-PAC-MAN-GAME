from tkinter import *
import random

GRID_SIZE = 21        # 21x21 grid (odd better for centered start)
CELL_SIZE = 25        # pixels
AGENT_SIZE = 15       # diameter in pixels

class Create_Grid:
    def __init__(self, root):
        self.root = root
        self.canvas = Canvas(root,
                             width=GRID_SIZE*CELL_SIZE,
                             height=GRID_SIZE*CELL_SIZE,
                             bg="white")
        self.canvas.pack()
        # Maze matrix: wall only when BOTH row and col are odd -> corridors remain
        self.maze = self.generate_maze()
        # Draw maze
        self.draw_maze()

    def generate_maze(self):
        """
        Create a grid where: wall if (row % 2 == 1 and col % 2 == 1)
        This leaves corridors (paths) for adjacent movement.
        """
        maze = []
        for r in range(GRID_SIZE):
            row = []
            for c in range(GRID_SIZE):
                if (r % 2 == 1) and (c % 2 == 1):
                    row.append(1)  # wall (black block)
                else:
                    row.append(0)  # path (walkable)
            maze.append(row)
        return maze
    def draw_maze(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                x0, y0 = c*CELL_SIZE, r*CELL_SIZE
                x1, y1 = x0+CELL_SIZE, y0+CELL_SIZE
                if self.maze[r][c] == 1:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="black", outline="")
                else:
                    self.canvas.create_rectangle(x0, y0, x1, y1, fill="white", outline="")


