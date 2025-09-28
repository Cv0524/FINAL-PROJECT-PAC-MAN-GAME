from turtle import Turtle, Screen
import time
from snake import Snake
s = Turtle()
screen = Screen()
screen.setup(width=600, height=600)
screen.title("My Snake Game")
screen.bgcolor("black")
screen.tracer(0)

snake = Snake()
screen.listen()

screen.onkey(key="w", fun=snake.moved_up)
screen.onkey(key="s", fun=snake.moved_down)
screen.onkey(key="a", fun=snake.moved_left)
screen.onkey(key="d", fun=snake.moved_rigth)

while True:
    screen.update()
    time.sleep(0.07)
    snake.moved()


screen.exitonclick()