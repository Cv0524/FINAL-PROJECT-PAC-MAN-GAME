from turtle import Turtle, Screen
from paddle import Paddle
from ball import Ball
import time
from score_board import Scoreboard
screen = Screen()
paddle = Turtle()
screen.setup(width=800, height=600)
screen.title("Paddle Game")
screen.bgcolor("black")
screen.tracer(0)



paddle1 = Paddle((350,0))
paddle1.color("red")
paddle2 = Paddle((-350,0))
paddle1.color("yellow")
ball = Ball()
score = Scoreboard() 


screen.listen()
screen.onkey(fun=paddle1.go_up, key="w")
screen.onkey(fun=paddle1.go_down, key="s")

screen.onkey(fun=paddle2.go_up, key="o")
screen.onkey(fun=paddle2.go_down, key="l")


target_score = 2
new_paddle1_score = 0
new_paddle2_score = 0

game_on = True


while game_on:
    time.sleep(ball.move_speed)
    screen.update()
    ball.move()

    if ball.ycor() > 280 or ball.ycor() < -280:
        #needs to be bounce
        ball.bounce_y()
    if ball.distance(paddle1) < 50 and ball.xcor() > 320 : 
        print("Contact! 1")
        ball.bounce_x()

        
    if ball.distance(paddle2) < 50 and ball.xcor() < -320:
        print("Contact! 2")
        ball.bounce_x()


    # Detect paddle1  misses
    if ball.xcor() > 350:
        ball.reset_position()
        score.paddle1_point()

    if ball.xcor() < -380:
        ball.reset_position()
        score.paddle2_point()
   






screen.exitonclick()