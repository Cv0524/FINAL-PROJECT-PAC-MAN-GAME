from tkinter import *
from grid import Create_Grid
from agent import Agent

if __name__ == "__main__":
    root = Tk()
    root.title("Pacman Game with Multi Agent")

    # Create grid
    app = Create_Grid(root)

    # Add agents (you can spawn more with different colors)
    agent1 = Agent(root, app.canvas, app.maze, color="red")
    agent2 = Agent(root, app.canvas, app.maze, color="blue")
    agent3 = Agent(root, app.canvas, app.maze, color="green")

    root.mainloop()
