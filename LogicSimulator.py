import pygame
from Mover import Mover
import math
import random

def GetPos(X,Y,Z):
    Mov = Mover(0,0,0)
    Mov.Forward(-Z)
    Mov.Right(120)
    Mov.Forward(X)
    Mov.Left(240)
    Mov.Forward(Y)
    return (Mov.X,Mov.Y)

def RenderGate(Enabled,Size=10,Color=(128,128,128)):
    CanSize = math.ceil(GetPos(0,0,0)[1]*Size - GetPos(1,1,1)[1]*Size)
    def TransformPos(Pos):
        X,Y = Pos
        X *= Size
        Y *= Size
        X += CanSize/2
        Y += CanSize
        return (X,Y)
    Surface = pygame.surface.Surface((CanSize,CanSize))
    Surface = Surface.convert_alpha()
    Surface.fill((255,255,255,0))
    
    Darker = (Color[0] * 0.9, Color[1] * 0.9, Color[2] * 0.9)
    Lighter = (min(255,Color[0] * 1.1), min(255,Color[1] * 1.1), min(255,Color[2] * 1.1))
    
    pygame.draw.polygon(Surface,Darker,list(map(TransformPos,[GetPos(0,0,0),GetPos(1,0,0),GetPos(1,0,1),GetPos(0,0,1)])))
    pygame.draw.polygon(Surface,Color,list(map(TransformPos,[GetPos(0,0,0),GetPos(0,1,0),GetPos(0,1,1),GetPos(0,0,1)])))
    pygame.draw.polygon(Surface,Lighter,list(map(TransformPos,[GetPos(0,0,1),GetPos(1,0,1),GetPos(1,1,1),GetPos(0,1,1)])))
    
    if Enabled == False:
        Color = (0,0,0)
    else:
        Color = (128,255,255)
    pygame.draw.polygon(Surface,Color,list(map(TransformPos,[GetPos(0.1,0,0.1),GetPos(0.9,0,0.1),GetPos(0.9,0,0.9),GetPos(0.1,0,0.9)])))
    pygame.draw.polygon(Surface,Color,list(map(TransformPos,[GetPos(0,0.1,0.1),GetPos(0,0.9,0.1),GetPos(0,0.9,0.9),GetPos(0,0.1,0.9)])))
    pygame.draw.polygon(Surface,Color,list(map(TransformPos,[GetPos(0.1,0.1,1),GetPos(0.9,0.1,1),GetPos(0.9,0.9,1),GetPos(0.1,0.9,1)])))
    return Surface
    
def DistanceSort(Gate):
    return sum(Gate[2]) + random.uniform(-0.1,0.1)


Gates = [[False,(128,128,128),(0,0,0)],[True,(255,0,0),(1,0,0)],[False,(255,128,0),(0,1,0)]]

def ShowGates(Gates):
    Screen = pygame.display.set_mode((500,500),pygame.RESIZABLE)
    Clock = pygame.time.Clock()
    pygame.display.set_caption("Logic Viewer")

    Running = True
    while Running:
        Events = pygame.event.get()
        for Event in Events:
            if Event.type == pygame.QUIT:
                Running = False
        if Running == False:
            break
                
        Screen.fill((200,200,200))
        
        Gates.sort(key=DistanceSort)
        for Gate in Gates:
            X,Y,Z = Gate[2]
            X *= 20
            Y *= 20
            Z *= 20
            X,Y = GetPos(-Y,-X,Z)
            X += Screen.get_width()/2
            Y += Screen.get_height()/2
            
            Screen.blit(RenderGate(Gate[0],Size=20,Color=Gate[1]),(X,Y))
        
        pygame.display.update()
        Clock.tick(60)
    pygame.quit()
