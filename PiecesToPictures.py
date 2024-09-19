import pygame
from pygame import Rect
from pygame.math import Vector2
import random


class Tile():
    def __init__(self,grid,rect,position,status,points=0,speed=0.3):
        self.textureGrid = grid
        self.textureRect = rect
        self.position = position
        self.endPosition = position
        self.status = status
        self.points = points
        self.speed = speed
        self.moveVector = Vector2(0,0)
    def findEndPosition(self,vector,state):
        newPosition = self.position + vector
        while True:
            newPosition = newPosition + vector
            if len(state.board[0])<=newPosition.x>0 or len(state.board)<=newPosition.y>0\
                or state.board[int(newPosition.x)][(int(newPosition.y))] !=0:
                break
        self.endPosition = newPosition
    
class MoveTile():
    def __init__ (self,tile,state):
        self.tile = tile
        self.newPosition = self.tile.position + (self.tile.moveVector * self.tile.speed)
        self.state = state
    def run(self):
        if self.tile.position == self.tile.endPosition\
            or self.newPosition == Vector2(0,0)\
            or self.newPosition.x < 0\
            or self.newPosition.x > self.state.cellCount\
            or self.newPosition.y < 0\
            or self.newPosition.y > self.state.cellCount:
            self.state.board[int(self.tile.position.x)][int(self.tile.position.y)] = self.tile
            self.tile.status = 'board'
        else:
            self.tile.position = self.newPosition
            
class NewTile():
    def __init__(self,state):
        self.state = state
    def run(self):
        if len(self.state.queue)>0 and self.state.board[1][0] == 0:
            tile = self.state.queue.pop(0)
            tile.moveVector = Vector2(1,0)
            tile.status = 'inflight'
            tile.findEndPosition(Vector2(1,0),self.state)
            self.state.board[int(tile.position.x)][int(tile.position.y)] = tile
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

        self.pictureSize = Vector2(self.gameState.level.pictureImage.get_size())
        self.pictureCellRatios = self.gameState.boardSize.elementwise() / self.pictureSize.elementwise()
        self.pictureCellRatio = max(self.pictureCellRatios.x,self.pictureCellRatios.y)
        self.pictureImage = pygame.transform.smoothscale(self.gameState.level.pictureImage, (self.pictureSize.x * self.pictureCellRatio, self.pictureSize.y * self.pictureCellRatio))
        self.pictureOffset = ((self.pictureSize.elementwise()*self.pictureCellRatio) - (self.gameState.cellSize.elementwise()*self.gameState.cellCount)).elementwise()//2
        self.newTileButtonImage = pygame.transform.smoothscale(self.theme.newTileButtonTexture, (150*4/self.gameState.cellCount, 150*4/self.gameState.cellCount))

        self.windowSize = self.gameState.worldSize
        self.window = pygame.display.set_mode((int(self.windowSize.x),int(self.windowSize.y)))
        textureRect = Rect(0, 0, int(self.gameState.cellSize.x),int(self.gameState.cellSize.y))
        self.newTileButton = Tile(Vector2(0,0),textureRect,Vector2(0,0),'button',0)

        self.NewTileQueue()
        self.NewBoard()

        self.commands = []

        # Loop properties
        self.clock = pygame.time.Clock()
        self.running = True

    def processInput(self):
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
                    self.commands.append(NewTile(self.gameState))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                #mouseClicked = True
                self.commands.append(NewTile(self.gameState))
                #mousePos = pygame.mouse.get_pos()
        
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
        self.gameState.board = [[0 for x in range(self.gameState.cellCount)] for y in range(self.gameState.cellCount)]

    def renderTile(self,tile):
        spritePoint = tile.position.elementwise()*self.gameState.cellSize + self.gameState.boardPosition
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
