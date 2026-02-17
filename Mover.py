import math

class Mover():
    def __init__(self,X,Y,Direction):
        self.X = X
        self.Y = Y
        self.Direction = Direction
    def Forward(self,Amount):
        self.X += math.sin(math.radians(self.Direction)) * Amount
        self.Y += math.cos(math.radians(self.Direction)) * Amount
    def Right(self,Angle):
        self.Direction -= Angle
    def Left(self,Angle):
        self.Direction += Angle
