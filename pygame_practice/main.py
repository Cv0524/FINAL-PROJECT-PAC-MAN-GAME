import pygame
import os
pygame.init()

WIDTH, HEIGHT = 900, 500
#SET UP SCREEN pygame.display.set_mode((WIDTH, HEIGHT))
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
#Create a title
pygame.display.set_caption("Game!")
bg_color = (255,255,255)

SPACESHIP_W , SPACESHIP_H = 40, 55
FPS = 60
VEL = 5

#LOAD THE IMAGE Y
YELLOW_SPACESHIP_IMG = pygame.image.load(
    os.path.join("pygame_practice/PygameForBeginners/Assets","spaceship_yellow.png"))
# RESIZE THE IMAGE AND ROTTATE
YELLOW_SPACESHIP = pygame.transform.rotate(
    pygame.transform.scale(YELLOW_SPACESHIP_IMG,
    (SPACESHIP_H,SPACESHIP_W)), 90)


#LOAD THE IMAGE R
RED_SPACESHIP_IMG = pygame.image.load(
    os.path.join("pygame_practice/PygameForBeginners/Assets","spaceship_red.png"))
# RESIZE THE IMAGE
RED_SPACESHIP = pygame.transform.rotate(
    pygame.transform.scale(
    RED_SPACESHIP_IMG,(SPACESHIP_H,SPACESHIP_W)), 270)



def draw_window(yellow, red):
    WIN.fill((bg_color))
    #Place the image the to screen using "blit"
    # Calling the spaceship yellow
    """
        yellow.x,yellow.y are the coordinates in the main function coordinates
    """
    WIN.blit(YELLOW_SPACESHIP,(yellow.x,yellow.y))
    # Calling the spaceship Red
    WIN.blit(RED_SPACESHIP,(red.x,red.y))
    #update the display for every changes
    pygame.display.update()


def main():
    # Create a coordinates to move the spaceship
    """
    Rect is to store coordinates value 
    in tuples also to place Width and Heigth exmaple (x= 100, y=300, width, heigth)
    """
    yellow = pygame.Rect(100, 300, SPACESHIP_H, SPACESHIP_H)
    red = pygame.Rect(700, 300, SPACESHIP_H, SPACESHIP_H)

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run =False

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_a]: #left
            yellow.x -= VEL
        if key_pressed[pygame.K_d]: #left
            yellow.x += VEL
        if key_pressed[pygame.K_w]: #left
            yellow.y -= VEL
        if key_pressed[pygame.K_s]: #left
            yellow.y += VEL

        # Adding x coordinates per iteration from the loop
        #yellow.x += 5
        # Calling the draw function and passing the y coordinates and red cooordinates
        draw_window(yellow,red)

        # if yellow.x > 900:
        #     print("Outside the frame")
        #     run = False

    pygame.quit()


if __name__ == "__main__":
    main()
