import random
import pygame

CELL_SIZE = 50
STEP = 5  # how many pixels to move per frame

class Agent:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 15
        self.direction = random.choice([(STEP,0), (-STEP,0), (0,STEP), (0,-STEP)])  

    def move(self, walls):
        # Try moving
        new_x = self.x + self.direction[0]
        new_y = self.y + self.direction[1]
        new_rect = pygame.Rect(new_x - self.radius, new_y - self.radius,
                               self.radius*2, self.radius*2)

        # Check collision with walls
        if not any(new_rect.colliderect(w) for w in walls): 
            # No collision → update position
            self.x = new_x
            self.y = new_y
        else:
            # Collision → pick a new random direction
            self.direction = random.choice([(STEP,0), (-STEP,0), (0,STEP), (0,-STEP)])

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
