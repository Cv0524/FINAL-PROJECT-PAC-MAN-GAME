import tkinter as tk
import random
import time

# Constants
CELL_SIZE = 40
EASY_GRID_SIZE = 10
MEDIUM_GRID_SIZE = 15
HARD_GRID_SIZE = 20
START = (0, 0)

# Global variable for root window
root = None

class MazeSolver:
    def __init__(self, master, grid_size):
        self.master = master
        self.grid_size = grid_size

        # Canvas for drawing the maze
        self.canvas = tk.Canvas(master, width=grid_size * CELL_SIZE, height=grid_size * CELL_SIZE, bg="white")
        self.canvas.pack()

        # Initialize the grid with walls
        self.grid = [[1 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.end = (grid_size - 1, grid_size - 1)
        self.create_maze()
        self.draw_maze()

        # Timer
        self.start_time = time.time()
        self.timer_label = tk.Label(master, text="Time: 0 sec", font=("Arial", 12))
        self.timer_label.pack(side=tk.TOP, pady=5)
        self.update_timer()  # Start the timer

        # Player
        self.player_position = list(START)
        self.canvas.bind("<Key>", self.move_player)
        self.canvas.focus_set()
        self.draw_player()

    def create_maze(self):
        # Create a solvable maze using recursive backtracking
        self._recursive_backtrack(0, 0)
        self.grid[START[0]][START[1]] = 0  # Start point
        self.grid[self.end[0]][self.end[1]] = 0  # End point

    def _recursive_backtrack(self, x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size and self.grid[nx][ny] == 1:
                self.grid[nx][ny] = 0
                self.grid[x + dx][y + dy] = 0
                self._recursive_backtrack(nx, ny)

    def draw_maze(self):
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                color = "black" if self.grid[y][x] == 1 else "white"
                self.canvas.create_rectangle(
                    x * CELL_SIZE, y * CELL_SIZE,
                    (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                    fill=color
                )

        # Draw start and end points
        self.canvas.create_rectangle(
            START[1] * CELL_SIZE, START[0] * CELL_SIZE,
            (START[1] + 1) * CELL_SIZE, (START[0] + 1) * CELL_SIZE,
            fill="green"
        )
        self.canvas.create_rectangle(
            self.end[1] * CELL_SIZE, self.end[0] * CELL_SIZE,
            (self.end[1] + 1) * CELL_SIZE, (self.end[0] + 1) * CELL_SIZE,
            fill="red"
        )

    def draw_player(self):
        self.canvas.delete("player")
        self.canvas.create_oval(
            self.player_position[1] * CELL_SIZE + 5,
            self.player_position[0] * CELL_SIZE + 5,
            (self.player_position[1] + 1) * CELL_SIZE - 5,
            (self.player_position[0] + 1) * CELL_SIZE - 5,
            fill="blue", tags="player"
        )

    def move_player(self, event):
        if event.keysym == 'Up':
            new_position = (self.player_position[0] - 1, self.player_position[1])
        elif event.keysym == 'Down':
            new_position = (self.player_position[0] + 1, self.player_position[1])
        elif event.keysym == 'Left':
            new_position = (self.player_position[0], self.player_position[1] - 1)
        elif event.keysym == 'Right':
            new_position = (self.player_position[0], self.player_position[1] + 1)
        else:
            return

        if self.is_move_valid(new_position):
            self.player_position = list(new_position)
            self.draw_player()
            self.check_win()

    def is_move_valid(self, position):
        x, y = position
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size and self.grid[x][y] == 0

    def check_win(self):
        if tuple(self.player_position) == self.end:
            elapsed_time = round(time.time() - self.start_time, 2)
            self.canvas.create_text(
                self.grid_size * CELL_SIZE // 2,
                self.grid_size * CELL_SIZE // 2,
                text=f"Congratulations! You've solved the maze in {elapsed_time} seconds!",
                fill="orange",  # Changed color for visibility
                font=("Arial", 16)
            )

    def update_timer(self):
        elapsed_time = round(time.time() - self.start_time, 2)
        self.timer_label.config(text=f"Time: {elapsed_time} sec")
        self.master.after(1000, self.update_timer)

def start_game(level):
    global root
    root.destroy()  # Clear the previous game instance
    root = tk.Tk()
    root.title("Maze Game")
    if level == "Easy":
        MazeSolver(root, EASY_GRID_SIZE)
    elif level == "Medium":
        MazeSolver(root, MEDIUM_GRID_SIZE)
    elif level == "Hard":
        MazeSolver(root, HARD_GRID_SIZE)
    root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Maze Game")

    tk.Label(root, text="Select Difficulty Level:", font=("Arial", 14)).pack(pady=10)
    tk.Button(root, text="Easy", command=lambda: start_game("Easy")).pack(pady=5)
    tk.Button(root, text="Medium", command=lambda: start_game("Medium")).pack(pady=5)
    tk.Button(root, text="Hard", command=lambda: start_game("Hard")).pack(pady=5)

    root.mainloop()