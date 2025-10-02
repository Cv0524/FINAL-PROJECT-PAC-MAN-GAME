from tkinter import *
import random

GRID_SIZE = 21        # 21x21 grid (odd better for centered start)
CELL_SIZE = 25        # pixels
AGENT_SIZE = 15       # diameter in pixels

class GridApp:
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

        # Start agent at center (should be a path)
        self.agent_row, self.agent_col = GRID_SIZE//2, GRID_SIZE//2
        if self.maze[self.agent_row][self.agent_col] == 1:  # fallback if center is wall
            self.agent_row, self.agent_col = 0, 0
        self.agent = self.create_agent(self.agent_row, self.agent_col)

        # Start automatic random movement
        self.random_move()

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

    def create_agent(self, row, col):
        x0 = col*CELL_SIZE + (CELL_SIZE-AGENT_SIZE)//2
        y0 = row*CELL_SIZE + (CELL_SIZE-AGENT_SIZE)//2
        x1 = x0 + AGENT_SIZE
        y1 = y0 + AGENT_SIZE
        return self.canvas.create_oval(x0, y0, x1, y1, fill="red")

    def move_agent(self, new_row, new_col):
        if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
            if self.maze[new_row][new_col] == 0:  # only move if path
                dx = (new_col - self.agent_col) * CELL_SIZE
                dy = (new_row - self.agent_row) * CELL_SIZE
                self.canvas.move(self.agent, dx, dy)
                self.agent_row, self.agent_col = new_row, new_col

    def random_move(self):
        """Try random directions and move to the first valid path neighbor."""
        directions = [(-1,0), (1,0), (0,-1), (0,1)]  # up, down, left, right
        random.shuffle(directions)

        for dr, dc in directions:
            new_row = self.agent_row + dr
            new_col = self.agent_col + dc
            if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                if self.maze[new_row][new_col] == 0:
                    self.move_agent(new_row, new_col)
                    break

        # call again after 200 ms
        self.root.after(200, self.random_move)

if __name__ == "__main__":
    root = Tk()
    root.title("Random-moving Agent - Maze (odd walls, even paths visual)")
    app = GridApp(root)
    root.mainloop()
