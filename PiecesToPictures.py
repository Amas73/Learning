import os
import random
import pygame
from pygame import Rect
from pygame.math import Vector2
from PIL import Image


class GameState():
    def __init__(self):
        self.worldSize = Vector2(640,896)
        self.boardSize = Vector2(600,600)
        self.boardPosition = Vector2(30,200)


class GameLevel():
    def __init__(self):
        self.tileQueue = []
        # Level variables
        self.randomSeed = 10                                                              ####################################
        self.gameDifficulty = 'Normal'                                                    #########  testing values  #########
        self.pictureImage = pygame.image.load("avengers.jpg")                             ####################################
        
        

class Command():
    def run(self):
        raise NotImplementedError()

# class NewTileCommand(Command):
#     def __init__(self,state):
#         self.state = state
#     def run(self):
#         self.unit.lastBulletEpoch = self.state.epoch
#         self.state.bullets.append(Bullet(self.state,self.unit))
    

class UserInterface():
    def __init__(self):
        pygame.init()
        
        # Game state
        self.inGame = True
        self.gameLevel = 0
        self.gameState = GameState()

        # Rendering properties
        random.seed(randomSeed)
        self.difficulties = {'Easy': [4,150], 'Normal': [5,120], 'Harder': [6,100], 'Hardest': [7,85]}
        self.cellSize = Vector2(self.difficulties[self.gameDifficulty][1],self.difficulties[self.gameDifficulty][1])
        self.pictureSize = Vector2(self.pictureImage.get_size())
        self.pictureCellRatios = self.gameState.boardSize.elementwise() / self.pictureSize.elementwise()
        self.pictureCellRatio = max(self.pictureCellRatio.x,self.pictureCellRatio.y)
        self.pictureImage = pygame.transform.smoothscale(self.pictureImage, self.pictureSize.x * self.pictureCellRatio, self.pictureSize.y * self.pictureCellRatio)


        # Tile queue

        
        # Window
        windowSize = self.gameState.worldSize
        pygame.display.set_caption("Pieces to Pictures")
        pygame.display.set_icon(pygame.image.load("icon80.png"))
        self.window = pygame.display.set_mode((int(windowSize.x),int(windowSize.y)))
        
        # Controls
        self.newTile = self.gameState.tiles.pop(0)
        self.commands = []
        
        # Loop properties
        self.clock = pygame.time.Clock()
        self.running = True
        
    @property
    def cellWidth(self):
        return int(self.cellSize.x)

    @property
    def cellHeight(self):
        return int(self.cellSize.y)

    def processInput(self):
        self.moveTileCommand = Vector2(0,0)
        mouseClicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pygame.K_RIGHT:
                    self.moveTileCommand.x = 1
                elif event.key == pygame.K_LEFT:
                    self.moveTileCommand.x = -1
                elif event.key == pygame.K_DOWN:
                    self.moveTileCommand.y = 1
                elif event.key == pygame.K_UP:
                    self.moveTileCommand.y = -1
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouseClicked = True
                
        # Shoot if left mouse was clicked
        if mouseClicked:
            self.commands.append(
                NewTileCommand(self.gameState,self.newTile)
            )
                    
    def update(self):
        self.gameState.update(self.moveTileCommand)
        
    def render(self):
        self.window.fill((0,0,0))
        
        pygame.display.update()    
        
    def run(self):
        while self.inGame:
            self.gameLevel = GameLevel()
            while self.running:
                self.processInput()
                #self.update()
                self.render()
                self.clock.tick(60)



userInterface = UserInterface()
userInterface.run()

pygame.quit()