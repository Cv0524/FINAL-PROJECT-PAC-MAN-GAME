import random
import pygame
# pygame setup
pygame.init()
screen = pygame.display.set_mode((800, 800))


class Agents():
    def __init__(self,screen,color):
        self.screen = screen
        self.color = color
        self.radius = 20
    def draw_circle(self,x_cor,y_cor):
        pygame.draw.circle(self.screen, (self.color), (x_cor,y_cor) , self.radius)
