from turtle import Turtle


x_position = [0, -20, -40]
y_position = [0, -0, -0]
starting = 3
MOVE_DISTANCE = 20
DOWN = 90
UP = 270
LEFT = 180
RIGHT = 0
class Snake:
    def __init__(self):
        self.segments = []
        self.create_snake()
        self.head = self.segments[0]

    def create_snake(self):
        #create a 3 turtl
        for turttle_index in range(0,starting):
            new_turtle = Turtle(shape="square")
            new_turtle.shapesize(0.7)
            new_turtle.color("white")
            new_turtle.penup()
            new_turtle.goto(x=x_position[turttle_index], y = y_position[turttle_index])
            self.segments.append(new_turtle)
    def extend(sef)

    def moved(self):
        for turtle_segments in range(len(self.segments) -1, 0, -1):
            new_x = self.segments[turtle_segments - 1].xcor()
            new_y = self.segments[turtle_segments - 1].ycor()
            self.segments[turtle_segments].goto(new_x, new_y)
        self.head.forward(MOVE_DISTANCE)
        #self.segments[0].left(90)

    def moved_up(self):
        if self.head.heading() != DOWN:
            self.head.setheading(90)
    def moved_down(self):
        if self.head.heading() != UP:
            self.head.setheading(270)
    def moved_left(self):
        if self.head.heading() != RIGHT:
            self.head.setheading(180)
    def moved_rigth(self):
        if self.head.heading() != LEFT:
            self.head.setheading(0)