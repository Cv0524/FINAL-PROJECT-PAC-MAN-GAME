import pygame

pygame.init()
CELL_SIZE = 50

maze_layout = [
    "################",
    "#..............#",
    "#.####..####...#",
    "................",
    "....#.#..#.#..#.",
    "#.###.####.####.",
    "#...#......#....#",
    "#...#.#.#..#..#.",
    "#.#####.####..#.",
    "#...............",
    "#.####..####...#",
    "................",
    "....#.#..#.#..#.",
    "#.#.#.####.####.",
    "#...#......#....#",
    "#################"
]

class Maze:
    def __init__(self, screen):
        self.screen = screen
        self.walls = []  # store wall rectangles

        # Build wall list from layout
        for row_idx, row in enumerate(maze_layout):
            for col_idx, cell in enumerate(row):
                if cell == "#":
                    rect = pygame.Rect(col_idx * CELL_SIZE,
                                       row_idx * CELL_SIZE,
                                       CELL_SIZE,
                                       CELL_SIZE)
                    self.walls.append(rect)

    def draw_maze(self):
        # Draw all walls
        for wall in self.walls:
            pygame.draw.rect(self.screen, (111, 111, 111), wall)  

