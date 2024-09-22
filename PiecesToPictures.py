import pygame
from pygame import Rect
from pygame.math import Vector2
import random
from copy import copy
from math import copysign

def vectorInt(vector: Vector2) -> Vector2:
    return Vector2(int(vector.x), int(vector.y))


class Tile():
    def __init__(self,grid,rect,position,status,points=0,speed=0.3):
        self.textureGrid = grid
        self.textureRect = rect
        self.position = position
        self.endPosition = copy(position)
        self.status = status
        self.points = points
        self.speed = speed
        self.moveVector = Vector2(0,0)
    def findEndPosition(self,state):
        newPosition = copy(self.position)
        while True:
            testedPosition = copy(newPosition)
            newPosition += self.moveVector
            if newPosition == Vector2(0,0)\
                or newPosition.x<0 or newPosition.x>=len(state.board)\
                or newPosition.y<0 or newPosition.y>=len(state.board[0])\
                or state.board[int(newPosition.x)][(int(newPosition.y))] !=0:
                break
        self.endPosition = testedPosition
    
class MoveTile():
    def __init__ (self,tile,state):
        self.tile = tile
        self.tile.position += (self.tile.moveVector * self.tile.speed)
        self.state = state
    def run(self):
        if vectorInt(self.tile.position) == self.tile.endPosition:
            self.tile.position = copy(self.tile.endPosition)
            self.state.board[int(self.tile.position.x)][int(self.tile.position.y)] = self.tile
            self.tile.status = 'board'
            
class NewTile():
    def __init__(self,state):
        self.state = state
    def run(self):
        if len(self.state.queue)>0 and self.state.board[1][0] == 0:
            tile = self.state.queue.pop(0)
            tile.moveVector = Vector2(1,0)
            tile.status = 'inflight'
            tile.findEndPosition(self.state)
            self.state.inFlightTiles.append(tile)

class RemoveNonInflightTiles():
    def __init__(self,itemList):
        self.itemList = itemList
    def run(self):
        newList = [ item for item in self.itemList if item.status == "inflight" ]
        self.itemList[:] = newList
        


class GameLevel():
    def __init__(self):
        self.difficulties = {'Easy': [4,150], 'Normal': [5,120], 'Harder': [6,100], 'Hardest': [7,85]}
        self.gameDifficulty = 'Normal'
        self.pictureImage = pygame.image.load("avengers.jpg") 


class ThemeGraphics():
    def __init__(self):
        self.newTileButtonTexture = pygame.image.load("Arrow.jpg")


class GameState(GameLevel):
    def __init__(self):
        self.level = GameLevel()
        self.cellCount = self.level.difficulties[self.level.gameDifficulty][0]
        self.cellSize = Vector2(self.level.difficulties[self.level.gameDifficulty][1],self.level.difficulties[self.level.gameDifficulty][1])
        self.worldSize = Vector2(700,1024)
        self.boardSize = Vector2(self.cellSize.x*self.cellCount,self.cellSize.y*(self.cellCount+1))
        self.boardPosition = Vector2(80,200)
        self.queue = []
        self.board = []
        self.inFlightTiles = []

class UserInterface():
    def __init__(self):
        pygame.init()
        
        # Game state
        self.gameState = GameState()
        self.theme = ThemeGraphics()

        self.windowSize = self.gameState.worldSize
        self.window = pygame.display.set_mode((int(self.windowSize.x),int(self.windowSize.y)))
        self.boardRect = Rect(self.gameState.boardPosition,self.gameState.boardSize)
        
        self.pictureSize = Vector2(self.gameState.level.pictureImage.get_size())
        self.pictureCellRatios = self.gameState.boardSize.elementwise() / self.pictureSize.elementwise()
        self.pictureCellRatio = max(self.pictureCellRatios.x,self.pictureCellRatios.y)
        self.pictureImage = pygame.transform.smoothscale(self.gameState.level.pictureImage, (self.pictureSize.x * self.pictureCellRatio, self.pictureSize.y * self.pictureCellRatio))
        self.pictureOffset = ((self.pictureSize.elementwise()*self.pictureCellRatio) - (self.gameState.cellSize.elementwise()*self.gameState.cellCount)).elementwise()//2
        
        self.newTileButtonImage = pygame.transform.smoothscale(self.theme.newTileButtonTexture, (150*4/self.gameState.cellCount, 150*4/self.gameState.cellCount))
        textureRect = Rect(0, 0, int(self.gameState.cellSize.x),int(self.gameState.cellSize.y))
        self.newTileButton = Tile(Vector2(0,0),textureRect,Vector2(0,0),'button',0)
        self.newTileButtonRect = Rect(self.gameState.boardPosition,self.gameState.cellSize)

        self.NewTileQueue()
        self.NewBoard()

        self.commands = []
        self.mousePosStart = ()

        # Loop properties
        self.clock = pygame.time.Clock()
        self.running = True

    def processInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    break
                elif event.key == pygame.K_SPACE:
                    self.commands.append(NewTile(self.gameState))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mousePosStart = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                mousePos = pygame.mouse.get_pos()
                if self.mousePosStart and self.boardRect.collidepoint(self.mousePosStart):
                    if self.newTileButtonRect.collidepoint(self.mousePosStart):
                        self.commands.append(NewTile(self.gameState))
                    else:
                        mouseVector = vectorInt((Vector2(self.mousePosStart[0],self.mousePosStart[1])-self.gameState.boardPosition) / self.gameState.cellSize.x)
                        if self.gameState.board[int(mouseVector.x)][int(mouseVector.y)] !=0:
                            moveX = int(mousePos[0]-self.mousePosStart[0])
                            moveY = int(mousePos[1]-self.mousePosStart[1])
                            if abs(moveX) > abs(moveY):
                                moveVector = Vector2(moveX//abs(moveX),0)
                            elif abs(moveY) > abs(moveX):
                                moveVector = Vector2(0,moveY//abs(moveY))
                            else:
                                moveVector = Vector2(0,0)
                            tile = self.gameState.board[int(mouseVector.x)][int(mouseVector.y)]
                            tile.moveVector = moveVector
                            tile.status = 'inflight'
                            tile.findEndPosition(self.gameState)
                            self.gameState.inFlightTiles.append(tile)
                            self.gameState.board[int(mouseVector.x)][int(mouseVector.y)] = 0
                    self.mousePosStart = ()
        
        self.commands.append(RemoveNonInflightTiles(self.gameState.inFlightTiles))

        for tile in self.gameState.inFlightTiles:
            if tile.status == 'inflight':
                self.commands.append(MoveTile(tile,self.gameState))
        

    def update(self):
        for command in self.commands:
            command.run()
        self.commands.clear()
    
    def NewTileQueue(self):
        for x in range(self.gameState.cellCount):
            for y in range(self.gameState.cellCount):
                unit = Vector2(x,y)
                position = Vector2(0,0)
                texturePoint = unit.elementwise()*self.gameState.cellSize + self.pictureOffset
                textureRect = Rect(int(texturePoint.x), int(texturePoint.y), int(self.gameState.cellSize.x),int(self.gameState.cellSize.y))
                self.gameState.queue.append(Tile(texturePoint,textureRect,position,'queue',10))
        random.shuffle(self.gameState.queue)

    def NewBoard(self):
        self.gameState.board = [[0 for x in range(self.gameState.cellCount+1)] for y in range(self.gameState.cellCount)]

    def renderBoard(self):
        pygame.draw.rect(self.window,(50,50,50),self.boardRect)
        for x in range(0,int(self.gameState.boardSize.y)+1,int(self.gameState.cellSize.x)):
            pygame.draw.line(self.window, (70,0,70),(x+self.gameState.boardPosition.x,self.gameState.boardPosition.y),(x+self.gameState.boardPosition.x,self.gameState.boardPosition.y+self.gameState.boardSize.y))
            pygame.draw.line(self.window, (70,0,70),(self.gameState.boardPosition.x,self.gameState.boardPosition.y+x),(self.gameState.boardPosition.x+self.gameState.boardSize.x,self.gameState.boardPosition.y+x))

    def renderTile(self,tile):
        spritePoint = tile.position.elementwise()*self.gameState.cellSize + self.gameState.boardPosition
        self.window.blit(self.pictureImage,spritePoint,tile.textureRect)


    def render(self):
        self.window.fill((0,0,0))
        self.renderBoard()

        for row in self.gameState.board:
            for tile in row:
                if tile != 0:
                    self.renderTile(tile)

        for tile in self.gameState.inFlightTiles:
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
