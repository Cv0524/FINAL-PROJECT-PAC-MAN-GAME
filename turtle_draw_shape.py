from turtle import Turtle, Screen
import heroes
import random
# initializing the turtle and screen objects
tim = Turtle()
#tim.shape("turtle")
tim.color("DarkOrchid4")

# for _ in range(4):
#     hero = heroes.gen()
#     print(hero)
# for _ in range(4):
#     tim.forward(300)
#     tim.right(90)
# Draw a dashed line
# for _ in range(15):
#     tim.forward(10)
#     tim.pendown()
#     tim.forward(10)
#     tim.penup()
#Draw a triangle


color = ["red","blue","green", 
         "yellow", "orange", "purple", 
         "pink","brown", "black"]

def draw_shape(num_sides):
    angle = 360 / num_sides
    for _ in range(num_sides):

        tim.forward(100)
        tim.right(angle)
        print(angle)

for num_sides in range(3, 11):
    tim.color(random.choice(color))
    draw_shape(num_sides)
    print(num_sides)
#Display the window until clicked
screen = Screen()
screen.exitonclick()