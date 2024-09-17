import os
import pygame
from pygame import Rect
from pygame.math import Vector2
import random


tiles = [Vector2(x,y) for x in range(5) for y in range(5)]

class Tile():
    def __init__(self,grid,rect,position,state,points):
        self.textureGrid = grid
        self.textureRect = rect
        self.position = position
        self.state = state
        self.points = points


class GameLevel():
    def __init__(self):
        self.gameDifficulty = 'Normal'
        self.pictureImage = pygame.image.load("avengers.jpg") 


class GameState():
    def __init__(self):
        self.worldSize = Vector2(700,896)
        self.boardSize = Vector2(600,600)
        self.boardPosition = Vector2(80,200)
        self.difficulties = {'Easy': [4,150], 'Normal': [5,120], 'Harder': [6,100], 'Hardest': [7,85]}
        self.queue = []
        self.board = []

    def NewTile(self):
        if len(self.queue)>0:
            tile = self.queue.pop(0)
            self.board[int(tile.position.x)][int(tile.position.y)] = tile


class UserInterface():
    def __init__(self):
        pygame.init()
        
        # Game state
        self.level = GameLevel()
        self.gameState = GameState()

        self.cellCount = self.gameState.difficulties[self.level.gameDifficulty][0]
        self.cellSize = Vector2(self.gameState.difficulties[self.level.gameDifficulty][1],self.gameState.difficulties[self.level.gameDifficulty][1])
        self.pictureSize = Vector2(self.level.pictureImage.get_size())
        self.pictureCellRatios = self.gameState.boardSize.elementwise() / self.pictureSize.elementwise()
        self.pictureCellRatio = max(self.pictureCellRatios.x,self.pictureCellRatios.y)
        self.pictureImage = pygame.transform.smoothscale(self.level.pictureImage, (self.pictureSize.x * self.pictureCellRatio, self.pictureSize.y * self.pictureCellRatio))
        self.pictureOffset = ((self.pictureSize.elementwise()*self.pictureCellRatio) - (self.cellSize.elementwise()*self.cellCount)).elementwise()//2

        self.windowSize = self.gameState.worldSize
        self.window = pygame.display.set_mode((int(self.windowSize.x),int(self.windowSize.y)))

        self.NewTileQueue()
        self.NewBoard()

        # Loop properties
        self.clock = pygame.time.Clock()
        self.running = True

    def processInput(self):
        self.moveTileCommand = Vector2(0,0)
        self.newTileCommand = False
        mouseClicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pygame.K_SPACE:
                    self.newTileCommand = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #mouseClicked = True
                self.newTileCommand = True

    def update(self):
        if self.newTileCommand:
            self.gameState.NewTile()

    def NewTileQueue(self):
        for x in range(self.gameState.difficulties[self.level.gameDifficulty][0]):
            for y in range(self.gameState.difficulties[self.level.gameDifficulty][0]):
                unit = Vector2(x,y)
                position = Vector2(0,0)
                texturePoint = unit.elementwise()*self.cellSize + self.pictureOffset
                textureRect = Rect(int(texturePoint.x), int(texturePoint.y), int(self.cellSize.x),int(self.cellSize.y))
                self.gameState.queue.append(Tile(texturePoint,textureRect,position,'queue',10))
        random.shuffle(self.gameState.queue)

    def NewBoard(self):
        self.gameState.board = [[0 for x in range(self.cellCount)] for y in range(self.cellCount)]

    def renderTile(self,tile):
        spritePoint = tile.position.elementwise()*self.cellSize + self.gameState.boardPosition
        self.window.blit(self.pictureImage,spritePoint,tile.textureRect)


    def render(self):
        self.window.fill((0,0,0))

        for row in self.gameState.board:
            for tile in row:
                if tile != 0:
                    self.renderTile(tile)

        pygame.display.update()   

    def run(self):
        while self.running:
            self.processInput()
            self.update()
            self.render()
            self.clock.tick(60)


ui = UserInterface()
ui.run()
