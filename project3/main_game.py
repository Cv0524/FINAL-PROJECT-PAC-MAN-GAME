from turtle import Screen
import time
from snake import Snake
from food import Food
from score_board import Scoreboard
screen = Screen()
screen.setup(width=600, height=600)
screen.title("My Snake Game")
screen.bgcolor("black")
screen.tracer(0)

snake = Snake()
food = Food()
score_board = Scoreboard()
screen.listen()

screen.onkey(key="w", fun=snake.moved_up)
screen.onkey(key="s", fun=snake.moved_down)
screen.onkey(key="a", fun=snake.moved_left)
screen.onkey(key="d", fun=snake.moved_rigth)

game_is_on = True

while game_is_on:
    screen.update()
    time.sleep(0.05)
    snake.moved()

    #Detect Collision with food
    if snake.head.distance(food) < 15:
        score_board.increase_score()
        print("Eaten!!!")
        food.refesh()
    if snake.head.xcor() > 290 or snake.head.xcor() < -290 or snake.head.ycor() > 290 or snake.head.ycor() < -290:
        game_is_on = False
        score_board.game_over()


screen.exitonclick()