import colorgram
from turtle import Turtle, Screen
import random
import turtle as t
t.colormode(255)
turtle = Turtle()
# colors = colorgram.extract('C:/MS COMPUTER SCIENCE TIPMC/MITELEC 101-MSCS11S1 - Special Topics AI AGENTS/coding_env/FINAL-PROJECT-PAC-MAN-GAME/project1/image.jpeg', 30)
# #print(colors)
# rgb_color = []
# for color in colors:
#     r = color.rgb.r
#     g = color.rgb.g
#     b = color.rgb.b
#     new_color = (r, g, b)
#     rgb_color.append(new_color)
# print(rgb_color)

color_list = [(172, 71, 36), 
              (227, 208, 117), (141, 145, 160), (95, 104, 135), (192, 151, 170), (183, 152, 41), 
              (32, 34, 14), (19, 26, 61), (97, 115, 173), (221, 172, 195), (173, 28, 9),
              (22, 36, 20), (121, 105, 113), (197, 98, 74), (234, 174, 160), (144, 151, 146), (101, 109, 103),
              (41, 51, 100), (182, 184, 214), (172, 104, 122), (46, 29, 45), (73, 72, 41), (232, 203, 16), 
              (121, 38, 50), (55, 71, 54)]
              
turtle.speed("fastest")
turtle.setheading(225)
turtle.penup()
turtle.forward(250)
turtle.setheading(0)
turtle.hideturtle()
number_of_dots = 100
for dot_count in range(1, number_of_dots + 1):
    turtle.dot(40, random.choice(color_list))
    turtle.forward(50)
    # turn to left
    if dot_count % 10 == 0:
        turtle.setheading(90)
        turtle.forward(50)
        turtle.setheading(180)
        turtle.forward(500)
        turtle.setheading(0)

screen = Screen()
screen.exitonclick()