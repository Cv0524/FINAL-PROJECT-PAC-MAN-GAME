from turtle import Turtle


class Scoreboard(Turtle):
    def __init__(self):
        super().__init__()
        self.color("white")
        self.penup()
        self.hideturtle()
        self.paddle1_score = 0
        self.paddle2_score = 0
        self.update_scoreborad()


    def update_scoreborad(self):
        self.clear()
        self.goto(-100,200)
        self.write(self.paddle1_score, align="center", font=("Courier", 50, "normal"))
        self.goto(100,200)
        self.write(self.paddle2_score, align="center", font=("Courier", 50, "normal"))
    def paddle1_point(self):
        self.paddle1_score += 1
        self.update_scoreborad()
    def paddle2_point(self):
        self.paddle2_score += 1
        self.update_scoreborad()
    
