import pygame

pygame.init()
CELL_SIZE = 50
"""
Maze layout
"""
maze_layout = [
    "################",
    "#..............#",
    "#.####..####...#",
    "#..............#",
    "#...#.#..#.#...#",
    "#.###.####.##.##",
    "#...#......#...#",
    "#...#.#.#..#...#",
    "#.#####.####..##",
    "#..............#",
    "#.####..####...#",
    "#.#............#",
    "#...#.#..#.##..#",
    "#.#.#.####.#..##",
    "#...#......#...#",
    "################"
]

class Maze:
    def __init__(self, screen):
        self.screen = screen
        self.walls = []  # store wall rectangles

        # Build wall list from layout
        """
        first loop is iterating the first index to the list item
        second loop is iterating all item in the first loop
        """
        for row_idx, row in enumerate(maze_layout):
            for col_idx, cell in enumerate(row):
                if cell == "#":
                    """
                        col_idx * CELL_SIZE: The left (x) position of the rectangle’s top-left corner; 
                            converts the column index on the grid into pixels from the left edge.
                        row_idx * CELL_SIZE: The top (y) position of the rectangle’s top-left corner; 
                            converts the row index into pixels from the top edge (y grows downward in Pygame).
                        CELL_SIZE: The rectangle’s width in pixels; one tile wide.
                        CELL_SIZE: The rectangle’s height in pixels; one tile tall (same as width for square tiles).
                    """
                    # storing rectangular coordinates
                    rect = pygame.Rect(col_idx * CELL_SIZE,
                                       row_idx * CELL_SIZE,
                                       CELL_SIZE,
                                       CELL_SIZE)
                    #store all coordinates in wall list variable
                    self.walls.append(rect)
    
    def draw_maze(self):
        # Draw all walls
        for wall in self.walls:
            pygame.draw.rect(self.screen, (111, 111, 111), wall)  

