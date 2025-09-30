import pygame
from maze import Maze
from agent import Agent
# pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 800))
running = True

vel = 5
screen_width, screen_height = screen.get_size()
maze = Maze(screen)


agents = [
    Agent(350, 500, (255,177,0)),  # yellow
    Agent(75, 80, (144,177,0)),    # green
    Agent(775, 400, (243,124,0))   # orange
]
clock = pygame.time.Clock()
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
                                            #V  H
    # pygame.draw.circle(screen, (255,177,0), (350,500) , 15)
    # pygame.draw.circle(screen, (144,177,0), (75,80) , 15)
    # pygame.draw.circle(screen, (243,124,0), (775,400) , 15)
            

    # Example: draw horizontal lines every 10px across screen height
    for x in range(0, screen_height, 50):
        pygame.draw.line(screen, (111,111,111), (0, x), (screen_width, x), 1)
    for y in range(0, screen_height, 50):
        pygame.draw.line(screen, (111,111,111), (y, 0), (y,screen_width), 1)

    #screen.fill((0, 0, 0))   # clear screen
    maze.draw_maze()       # draw maze



        # Update + draw agents
    for agent in agents:
        agent.move(maze.walls)
        agent.draw(screen)

    #pygame.display.flip()
    clock.tick(30)
    pygame.display.update()

pygame.quit()