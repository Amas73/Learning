import pygame
from pygame import Rect
from pygame.math import Vector2
import random
from copy import copy

def vectorInt(vector: Vector2) -> Vector2:
    return Vector2(int(vector.x), int(vector.y))


###############################################################################
#                               Game State                                    #
###############################################################################

class Tile():
    def __init__(self,state,tile,position,status,points=0,speed=0.3):
        self.state = state
        self.textureGrid = tile
        texturePoint = tile.elementwise()*self.state.cellSize + self.state.pictureOffset
        self.textureRect = Rect(texturePoint, (int(self.state.cellSize.x),int(self.state.cellSize.y)))
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
                state.board[int(testedPosition.x)][(int(testedPosition.y))] = self
                break
        self.endPosition = testedPosition

class GameLevel():
    def __init__(self):
        self.difficulties = {'Easy': [4,150], 'Normal': [5,120], 'Harder': [6,100], 'Hardest': [7,85]}
        self.gameDifficulty = 'Normal'
        self.pictureImage = pygame.image.load("avengers.jpg")
        #random.seed(22)

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
        self.pictureSize = Vector2(self.level.pictureImage.get_size())
        self.pictureCellRatios = self.boardSize.elementwise() / self.pictureSize.elementwise()
        self.pictureCellRatio = max(self.pictureCellRatios.x,self.pictureCellRatios.y)
        self.pictureImage = pygame.transform.smoothscale(self.level.pictureImage, (self.pictureSize.x * self.pictureCellRatio, self.pictureSize.y * self.pictureCellRatio))
        self.pictureOffset = ((self.pictureSize.elementwise()*self.pictureCellRatio) - (self.cellSize.elementwise()*self.cellCount)).elementwise()//2
        
        self.queue = []
        self.board = []
        self.inFlightTiles = []
        self.status = 'in game'


###############################################################################
#                                Commands                                     #
###############################################################################

class Command():
    def run(self):
        raise NotImplementedError()

class MoveTile(Command):
    def __init__ (self,tile,state):
        self.tile = tile
        self.tile.position += (self.tile.moveVector * self.tile.speed)
        self.state = state
    def run(self):
        if self.tile.position.x >= self.tile.endPosition.x - self.tile.speed\
            and self.tile.position.x <= self.tile.endPosition.x + self.tile.speed\
            and self.tile.position.y >= self.tile.endPosition.y - self.tile.speed\
            and self.tile.position.y <= self.tile.endPosition.y + self.tile.speed:
            self.tile.position = copy(self.tile.endPosition)
            self.tile.status = 'board'
            self.CheckComplete()
    def CheckComplete(self):
        if len(self.state.queue) == 0:
            complete = True
            for row in self.state.board:
                for tile in row[1:]:
                    if tile == 0 or tile.textureGrid != (tile.position + Vector2(0,-1)):
                        complete = False
                        break
        else:
            complete = False
        if complete:
            self.state.status = 'level complete'

         
class NewTile(Command):
    def __init__(self,state):
        self.state = state
    def run(self):
        if len(self.state.queue)>0 and self.state.board[1][0] == 0:
            tile = self.state.queue.pop(0)
            tile.moveVector = Vector2(1,0)
            tile.status = 'inflight'
            tile.findEndPosition(self.state)
            self.state.inFlightTiles.append(tile)

class RemoveNonInflightTiles(Command):
    def __init__(self,itemList):
        self.itemList = itemList
    def run(self):
        newList = [ item for item in self.itemList if item.status == "inflight" ]
        self.itemList[:] = newList
        


###############################################################################
#                             User Interface                                  #
###############################################################################

class UserInterface():
    def __init__(self):
        pygame.init()
        
        # Game state
        self.gameState = GameState()
        self.theme = ThemeGraphics()

        self.windowSize = self.gameState.worldSize
        self.window = pygame.display.set_mode((int(self.windowSize.x),int(self.windowSize.y)))
        self.boardRect = Rect(self.gameState.boardPosition,self.gameState.boardSize)
        
        self.newTileButtonImage = pygame.transform.smoothscale(self.theme.newTileButtonTexture, (150*4/self.gameState.cellCount, 150*4/self.gameState.cellCount))
        self.newTileButton = Tile(self.gameState,Vector2(0,0),Vector2(0,0),'button',0,0)
        self.newTileButton.textureRect = Rect(0,0, int(self.gameState.cellSize.x),int(self.gameState.cellSize.y))
        self.newTileButtonRect = Rect(self.gameState.boardPosition,self.gameState.cellSize)

        self.NewTileQueue()
        self.NewBoard()

        self.commands = []
        self.mousePosStart = ()

        # Loop properties
        self.clock = pygame.time.Clock()
        self.running = True

    def orthagonalVector(self,mouseStartPos,mouseEndPos):
        moveX = int(mouseEndPos[0]-mouseStartPos[0])
        moveY = int(mouseEndPos[1]-mouseStartPos[1])
        if abs(moveX) > abs(moveY):
            return Vector2(moveX//abs(moveX),0)
        elif abs(moveY) > abs(moveX):
            return Vector2(0,moveY//abs(moveY))
        else:
            return Vector2(0,0)

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
                            moveVector = self.orthagonalVector(self.mousePosStart,mousePos)
                            tile = self.gameState.board[int(mouseVector.x)][int(mouseVector.y)]
                            tile.moveVector = moveVector
                            tile.findEndPosition(self.gameState)
                            if tile.position != tile.endPosition:
                                tile.status = 'inflight'
                                self.gameState.inFlightTiles.append(tile)
                                self.gameState.board[int(mouseVector.x)][int(mouseVector.y)] = 0
                    
        self.commands.append(RemoveNonInflightTiles(self.gameState.inFlightTiles))

        for tile in self.gameState.inFlightTiles:
            if tile.status == 'inflight':
                self.commands.append(MoveTile(tile,self.gameState))
        
    def update(self):
        for command in self.commands:
            command.run()
        self.commands.clear()
        if self.gameState.status == 'level complete':
            self.running = False
    
    def NewTileQueue(self):
        for x in range(self.gameState.cellCount):
            for y in range(self.gameState.cellCount):
                unit = Vector2(x,y)
                position = Vector2(0,0)
                self.gameState.queue.append(Tile(self.gameState,unit,position,'queue',10))
        random.shuffle(self.gameState.queue)

    def NewBoard(self):
        self.gameState.board = [[0 for x in range(self.gameState.cellCount+1)] for y in range(self.gameState.cellCount)]


###############################################################################
#                                Rendering                                    #
###############################################################################
        
    def renderBoard(self):
        pygame.draw.rect(self.window,(50,50,50),self.boardRect)
        for x in range(0,int(self.gameState.boardSize.y)+1,int(self.gameState.cellSize.x)):
            pygame.draw.line(self.window, (70,0,70),(x+self.gameState.boardPosition.x,self.gameState.boardPosition.y),(x+self.gameState.boardPosition.x,self.gameState.boardPosition.y+self.gameState.boardSize.y))
            pygame.draw.line(self.window, (70,0,70),(self.gameState.boardPosition.x,self.gameState.boardPosition.y+x),(self.gameState.boardPosition.x+self.gameState.boardSize.x,self.gameState.boardPosition.y+x))

    def renderTile(self,tile):
        spritePoint = tile.position.elementwise()*self.gameState.cellSize + self.gameState.boardPosition
        self.window.blit(self.gameState.pictureImage,spritePoint,tile.textureRect)


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
            #self.CheckComplete()
            self.clock.tick(60)


###############################################################################
#                                Game Modes                                   #
###############################################################################

class GameMode():
    def processInput(self):
        raise NotImplementedError()
    def update(self):
        raise NotImplementedError()
    def render(self, window):
        raise NotImplementedError()

class MessageGameMode(GameMode):
    def __init__(self, ui, message):        
        self.ui = ui
        self.font = pygame.font.Font("BD_Cartoon_Shout.ttf", 36)
        self.message = message

    def processInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.ui.quitGame()
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE \
                or event.key == pygame.K_SPACE \
                or event.key == pygame.K_RETURN:
                    self.ui.showMenu()
                    
    def update(self):
        pass
        
    def render(self, window):
        surface = self.font.render(self.message, True, (200, 0, 0))
        x = (window.get_width() - surface.get_width()) // 2
        y = (window.get_height() - surface.get_height()) // 2
        window.blit(surface, (x, y))

class MenuGameMode(GameMode):
    def __init__(self, ui):        
        self.ui = ui
        
        # Font
        self.titleFont = pygame.font.Font("BD_Cartoon_Shout.ttf", 72)
        self.itemFont = pygame.font.Font("BD_Cartoon_Shout.ttf", 48)
        
        # Menu items
        self.menuItems = [
            {
                'title': 'Level 1',
                'action': lambda: self.ui.loadLevel("level1.tmx")
            },
            {
                'title': 'Level 2',
                'action': lambda: self.ui.loadLevel("level2.tmx")
            },
            {
                'title': 'Level 3',
                'action': lambda: self.ui.loadLevel("level3.tmx")
            },
            {
                'title': 'Quit',
                'action': lambda: self.ui.quitGame()
            }
        ]        

        # Compute menu width
        self.menuWidth = 0
        for item in self.menuItems:
            surface = self.itemFont.render(item['title'], True, (200, 0, 0))
            self.menuWidth = max(self.menuWidth, surface.get_width())
            item['surface'] = surface        
        
        self.currentMenuItem = 0
        self.menuCursor = pygame.image.load("cursor.png")        

    def processInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.ui.quitGame()
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.ui.showGame()
                elif event.key == pygame.K_DOWN:
                    if self.currentMenuItem < len(self.menuItems) - 1:
                        self.currentMenuItem += 1
                elif event.key == pygame.K_UP:
                    if self.currentMenuItem > 0:
                        self.currentMenuItem -= 1
                elif event.key == pygame.K_RETURN:
                    menuItem = self.menuItems[self.currentMenuItem]
                    try:
                        menuItem['action']()
                    except Exception as ex:
                        print(ex)
                    
    def update(self):
        pass
        
    def render(self, window):
        # Initial y
        y = 50
        
        # Title
        surface = self.titleFont.render("Pieces to Pictures", True, (200, 0, 0))
        x = (window.get_width() - surface.get_width()) // 2
        window.blit(surface, (x, y))
        y += (200 * surface.get_height()) // 100
        
        # Draw menu items
        x = (window.get_width() - self.menuWidth) // 2
        for index, item in enumerate(self.menuItems):
            # Item text
            surface = item['surface']
            window.blit(surface, (x, y))
            
            # Cursor
            if index == self.currentMenuItem:
                cursorX = x - self.menuCursor.get_width() - 10
                cursorY = y + (surface.get_height() - self.menuCursor.get_height()) // 2
                window.blit(self.menuCursor, (cursorX, cursorY))
            
            y += (120 * surface.get_height()) // 100           
            

class PlayGameMode(GameMode):
    def __init__(self, ui):
        pass


ui = UserInterface()
ui.run()

pygame.quit()
