from turtle import Turtle, Screen

turtle = Turtle()
screen = Screen()


# when "w" is pressed, move the turtle forward by 10 units
def move_forward():
    turtle.forward(10)
def move_backwards():
    turtle.backward(10)
def counter_clockwise():
    turtle.left(10)
def clockwise():
    turtle.right(10)
def clear_screen():
    #clear the line the frame
    turtle.clear()
    #pen up for path on the point
    turtle.penup()
    # back to the original coordinates or position of the point
    turtle.home()
    # pen down for new activity
    turtle.pendown()



# listen to the screen activity
screen.listen()
# reading keyboard input
screen.onkey(key="w", fun=move_forward)
screen.onkey(key="s", fun=move_backwards)
screen.onkey(key="a", fun=counter_clockwise)
screen.onkey(key="d", fun=clockwise)
screen.onkey(key="c", fun=clear_screen)




#key screen awake
screen.exitonclick()