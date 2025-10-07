import random

GRID_SIZE = 21
CELL_SIZE = 25
AGENT_SIZE = 20

class Agent:
    def __init__(self, root, canvas, maze, color="red"):
        self.root = root
        self.canvas = canvas
        self.maze = maze

        # Start agent at center (should be a path)
        self.agent_row, self.agent_col = GRID_SIZE // 2, GRID_SIZE // 2
        if self.maze[self.agent_row][self.agent_col] == 1:  # fallback if center is wall
            self.agent_row, self.agent_col = 0, 0

        # Create agent circle
        self.agent = self.create_agent(self.agent_row, self.agent_col, color)

        # Start automatic random movement
        self.random_move()

    def create_agent(self, row, col, color):
        x0 = col*CELL_SIZE + (CELL_SIZE-AGENT_SIZE)//2
        y0 = row*CELL_SIZE + (CELL_SIZE-AGENT_SIZE)//2
        x1 = x0 + AGENT_SIZE
        y1 = y0 + AGENT_SIZE
        return self.canvas.create_oval(x0, y0, x1, y1, fill=color)

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
