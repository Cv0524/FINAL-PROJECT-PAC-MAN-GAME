from turtle import Turtle, Screen
import random
import turtle as t
screen = Screen()
#Set up the size to the canvas
screen.setup(width=550,height=300)
t.hideturtle()
t.pensize(5)
t.setheading(315)
t.penup()
t.forward(280)
t.setheading(0)
t.pendown()
t.setheading(90)
for _ in range(20):
    t.forward(10)
    t.pendown()
    t.forward(10)
    t.penup()

# Get user input using textinput fucntion
user_bet = screen.textinput(title="Make your bet ", prompt="Which turtle will win: ")
color = ["red", "orange","yellow","green", "blue", "purple"]

#new turtle position
y_position = [-70, -40, -10, 20, 50, 80]

# store each turtle
all_turtle = []

#creating new turtle
for turtle_index in range(0,6):
    new_turtle = Turtle(shape="turtle")
    new_turtle.color(color[turtle_index])
    new_turtle.penup()
    #all turtle have same x while is different
    new_turtle.goto(x=-230, y = y_position[turtle_index])
    # atore all turle in all_turle list
    all_turtle.append(new_turtle)

# Starting the main loop
is_race_on = False
# verify the user input
if user_bet:
    is_race_on = True

while is_race_on:
    # looping each turtle in the list
    for turtle in all_turtle:
        if turtle.xcor() > 200:
            is_race_on = False
            winning_color = turtle.pencolor()
            if winning_color == user_bet:
                print(f"You won! The turtle {winning_color} is the winner")
            else:
                print(f"You lose! The turtle {winning_color} is the winner")
        
        # generating random distance or movement on each turple
        random_distance = random.randint(0, 10)
        # begin the movement on each turtle
        turtle.forward(random_distance)





screen.exitonclick()