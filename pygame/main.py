import pygame
from maze import Maze
from my_agents import Agents
# pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 800))
running = True

vel = 5
screen_width, screen_height = screen.get_size()
maze = Maze(screen)
color_value = (144,177,0)
#instantiate class with parameter
agent_one = Agents(screen,color=color_value)

def draw_lines():
    # Example: draw horizontal lines every 10px across screen height
    for x in range(0, screen_height, 50):
        pygame.draw.line(screen, (111,111,111), (0, x), (screen_width, x), 1)
    for y in range(0, screen_height, 50):
        pygame.draw.line(screen, (111,111,111), (y, 0), (y,screen_width), 1)
    
    


clock = pygame.time.Clock()
agent_one_cord = pygame.Rect(80,80,20,20)
VEL_X = 3
VEL_Y = 0


while running:
    clock.tick(60)

    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((0, 0, 0))
    draw_lines()

    # draw maze
    maze.draw_maze()
    agent_one_cord.x += VEL_X
    agent_one_cord.y += VEL_Y

    # if agent_one_cord.x >= 730:
    #     print("outside the loop!!")
    #     VEL_X = 0
    #     VEL_Y = 5
    #maze.walls contains all coordinates in the maze class
    for wall in maze.walls:
        if agent_one_cord.colliderect(wall):
            # Move agent out of wall to avoid sticking
            if VEL_X > 0:  # moving right, collided left side of wall
                agent_one_cord.right = wall.left
            elif VEL_X < 0:  # moving left, collided right side of wall
                agent_one_cord.left = wall.right

            if VEL_Y > 0:  # moving down, collided top side of wall
                agent_one_cord.bottom = wall.top
            elif VEL_Y < 0:  # moving up, collided bottom side of wall
                agent_one_cord.top = wall.bottom

            # Turn movement direction clockwise on collision
            if VEL_X != 0:
                VEL_Y = 3 if VEL_X > 0 else -2  # right→down, left→up
                VEL_X = 0
            elif VEL_Y != 0:
                VEL_X = -3 if VEL_Y > 0 else 2  # down→left, up→right
                VEL_Y = 0

            break  # only handle one collision per frame
            
            


    


            


   
    agent_one.draw_circle(agent_one_cord.x,agent_one_cord.y)
    pygame.display.update()

pygame.quit()