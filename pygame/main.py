import pygame
from maze import Maze
from my_agents import Agents

# pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 800))
running = True
clock = pygame.time.Clock()

# constants
screen_width, screen_height = screen.get_size()
VEL = 3  # base velocity

# create maze + agent
maze = Maze(screen)
AGENT1 = Agents(screen, color=(144, 177, 0), name="AGENT1")
AGENT1_cord = pygame.Rect(80, 80, 40, 40)  # bigger rect for circle center

# velocity direction
VEL_X = VEL
VEL_Y = 0


def draw_lines():
    for x in range(0, screen_height, 50):
        pygame.draw.line(screen, (50, 50, 50), (0, x), (screen_width, x), 1)
    for y in range(0, screen_width, 50):
        pygame.draw.line(screen, (50, 50, 50), (y, 0), (y, screen_height), 1)


while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))
    draw_lines()

    # draw maze
    maze.draw_maze()

    # move agent
    AGENT1_cord.x += VEL_X
    AGENT1_cord.y += VEL_Y

    # check collisions
    for wall in maze.walls:
        if AGENT1_cord.colliderect(wall):
            # push back
            if VEL_X > 0:  
                AGENT1_cord.right = wall.left
            elif VEL_X < 0:  
                AGENT1_cord.left = wall.right
            elif VEL_Y > 0:  
                AGENT1_cord.bottom = wall.top
            elif VEL_Y < 0:  
                AGENT1_cord.top = wall.bottom

            # turn clockwise
            if VEL_X != 0:  # moving horizontally → turn vertical
                VEL_Y = VEL if VEL_X > 0 else -VEL
                VEL_X = 0
            elif VEL_Y != 0:  # moving vertically → turn horizontal
                VEL_X = -VEL if VEL_Y > 0 else VEL
                VEL_Y = 0
            break

    # draw agent (circle centered in rect)
    AGENT1.draw_circle(AGENT1_cord.centerx, AGENT1_cord.centery)

    pygame.display.update()

pygame.quit()
