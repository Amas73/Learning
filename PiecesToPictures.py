import os
import pygame
from pygame import Rect
from pygame.math import Vector2
import random


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


class ThemeGraphics():
    def __init__(self):
        self.newTileButtonTexture = pygame.image.load("Arrow.png")
        self.test = 'Hello world!'


class GameState():
    def __init__(self):
        self.worldSize = Vector2(700,896)
        self.boardSize = Vector2(600,600)
        self.boardPosition = Vector2(80,200)
        self.difficulties = {'Easy': [4,150], 'Normal': [5,120], 'Harder': [6,100], 'Hardest': [7,85]}
        self.queue = []
        self.board = []

    def NewTile():
        def __init__(self):
            if len(self.queue)>0 and self.board[1][0] == 0:
                tile = self.queue.pop(0)
                self.board[int(tile.position.x)][int(tile.position.y)] = tile



class MoveTile():
    def __init__(tile,moveVector):
        currentPosition = tile.position
        newPosition = currentPosition + moveVector
        #if newPosition == Vector2(0,0) or newPosition.x < 0 or newPosition.x >= 


class AnimateTileMove():
    def __init__(tile,currentPosition,changeVector,endPosition):
        pass



class UserInterface():
    def __init__(self):
        pygame.init()
        
        # Game state
        self.level = GameLevel()
        self.gameState = GameState()
        self.theme = ThemeGraphics()

        self.cellCount = self.gameState.difficulties[self.level.gameDifficulty][0]
        self.cellSize = Vector2(self.gameState.difficulties[self.level.gameDifficulty][1],self.gameState.difficulties[self.level.gameDifficulty][1])
        self.pictureSize = Vector2(self.level.pictureImage.get_size())
        self.pictureCellRatios = self.gameState.boardSize.elementwise() / self.pictureSize.elementwise()
        self.pictureCellRatio = max(self.pictureCellRatios.x,self.pictureCellRatios.y)
        self.pictureImage = pygame.transform.smoothscale(self.level.pictureImage, (self.pictureSize.x * self.pictureCellRatio, self.pictureSize.y * self.pictureCellRatio))
        self.pictureOffset = ((self.pictureSize.elementwise()*self.pictureCellRatio) - (self.cellSize.elementwise()*self.cellCount)).elementwise()//2
        self.newTileButtonImage = pygame.transform.smoothscale(self.theme.newTileButtonTexture, ((150/4) * self.cellCount, (150/4) * self.cellCount))

        self.windowSize = self.gameState.worldSize
        self.window = pygame.display.set_mode((int(self.windowSize.x),int(self.windowSize.y)))
        textureRect = Rect(0, 0, int(self.cellSize.x),int(self.cellSize.y))
        self.newTileButton = Tile(Vector2(0,0),textureRect,Vector2(0,0),'button',0)

        self.NewTileQueue()
        self.NewBoard()

        self.commands = []

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
                command = self.gameState.NewTile()
                #mousePos = pygame.mouse.get_pos()
        self.commands.append(command)

    def update(self):
        for command in self.commands:
            command.run()
        self.commands.clear()
    
    def NewTileQueue(self):
        for x in range(self.cellCount):
            for y in range(self.cellCount):
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

        ### Render the New Tile Button
        self.window.blit(self.newTileButtonImage,self.gameState.boardPosition,self.newTileButton.textureRect)

        pygame.display.update()   

    def run(self):
        while self.running:
            self.processInput()
            self.update()
            self.render()
            self.clock.tick(60)


ui = UserInterface()
ui.run()

pygame.quit()
