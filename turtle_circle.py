from turtle import Turtle, Screen
from random import random
import turtle
import turtle as t
import random

t.colormode(255)
def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    random_color = (r, g, b)
    return random_color


def draw_spirograph(size_gap):
    for _ in range(int(360/size_gap)):
        turtle.color(random_color())
        turtle.speed("fastest")
        turtle.circle(100)
        current = turtle.heading()
        turtle.setheading(current + size_gap)
        turtle.circle(100)

draw_spirograph(10)








screen = Screen()
screen.exitonclick()