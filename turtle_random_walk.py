import random
from turtle import Turtle, Screen
import turtle as t
turtle = Turtle()
t.colormode(255)

color = ["red","blue","green", 
         "yellow", "orange", "purple", 
         "pink","brown", "black"]

# Function to generate a random color
def random_color():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    random_color = (r, g, b)
    return random_color

angles = [0, 90, 180, 270]
walk_distance = [3, 5, 7, 9, 11]

for _ in range(400):
    turtle.speed(30)
    #turtle.color(random.choice(color))
    turtle.color(random_color())
    turtle.pensize(15)
    turtle.right(random.choice(angles))
    turtle.forward(10)

screen = Screen()
screen.exitonclick()