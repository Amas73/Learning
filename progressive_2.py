import pygame
from pygame import Vector2
from pygame import Rect
import pygame_menu
from pygame_menu import themes
from copy import copy

def vectorInt(vector:Vector2) -> Vector2:
    return Vector2(int(vector.x), int(vector.y))


###############################################################################
#                               Game State                                    #
###############################################################################

class Tile():
    def __init__(self, imageFile:str, tile:Vector2, position:Vector2, angle:int=None):
        self.texture = imageFile
        self.textureGrid = tile
        self.position = position
        self.angle = angle
        self.currentFrame = 0
        
class MoveableTile(Tile):
    def __init__(self, imageFile:str, tile:Vector2, position:Vector2, angle:int=None, moveSpeed:float=0.3):
        super().__init__(imageFile,tile,position,angle)
        self.speed = moveSpeed
        self.endPosition = copy(self.position)
        self.moveVector = Vector2(0,0)
    def findEndPosition(self):
        self.endPosition = Vector2(3,0) # really is a calculation
        pass

class AnimatedTile(Tile):
    def __init__(self, imageFile:str, tile:Vector2, position:Vector2, maxFrame:int, angle:int=None, animateSpeed:float=0.2):
        super().__init__(imageFile,tile,position,angle)
        self.animationSpeed = animateSpeed
        self.maxFrame = maxFrame

class AnimatedOpenClosedTile(AnimatedTile):
    def __init__(self, imageFile:str, tile:Vector2, position:Vector2, maxFrame:int, angle:int=None, animateSpeed:float=0.2, openTime:float=0.2, closedTime:float=0.2):
        super().__init__(imageFile,tile,position,maxFrame,angle,animateSpeed)
        self.openTime = openTime
        self.closedTime = closedTime
        self.pauseState = 0

class MoveableAnimatedTile(Tile):
    def __init__(self, imageFile:str, tile:Vector2, position:Vector2, maxFrame:int, angle:int=None, moveSpeed:float=0.3, animateSpeed:float=0.2):
        super().__init__(imageFile,tile,position,angle)
        self.speed = moveSpeed
        self.endPosition = copy(self.position)
        self.moveVector = Vector2(0,0)
        self.animateSpeed = animateSpeed
        self.maxFrame = maxFrame

class MoveableAnimatedActionTile(MoveableAnimatedTile):
    def __init__(self, ui, imageFile:str, tile:Vector2, position:Vector2, maxFrame:int, angle:int=None, moveSpeed:float=0.3, animateSpeed:float=0.2):
        super().__init__(imageFile,tile,position,maxFrame,angle,moveSpeed,animateSpeed)
        self.ui = ui
        self.action = None
    def run(self):
        ui.commands.append(self.action)

class GameState():
    def __init__(self):
        self.cellSize = Vector2(140,140)
        self.boardPosition = Vector2(1.5*self.cellSize,2.5*self.cellSize)


###############################################################################
#                                Commands                                     #
###############################################################################

class Command():
    def run(self):
        raise NotImplementedError()

class AnimateTile(Command):
    def run(tile):
        tile.currentFrame += tile.animateSpeed
        if tile.currentFrame >= tile.maxFrame:
            if hasattr(tile,"action"):
                tile.run()
            else:
                tile.currentFrame = 0

class EndCommand(Command):
    def __init__(self, ui:object, tile:object):
        self.ui = ui
        self.tile = tile    
    def run(self):
        self.ui.running = False


###############################################################################
#                                Rendering                                    #
###############################################################################

class Layer():
    def __init__(self,cellSize):
        self.cellSize = cellSize
        
    @property
    def cellWidth(self):
        return int(self.cellSize.x)

    @property
    def cellHeight(self):
        return int(self.cellSize.y)         
    
    def renderTile(self,window,tile):
        spritePoint = tile.position.elementwise()*self.cellSize + self.gameState.boardPosition
        texturePoint = vectorInt(tile.textureGrid + Vector2(int(tile.currentFrame),0)).elementwise()*self.cellSize
        textureRect = Rect(int(texturePoint.x), int(texturePoint.y), self.cellWidth, self.cellHeight)
        texture = pygame.image.load(tile.texture)
        if tile.angle is None:
            window.blit(texture,spritePoint,textureRect)
        else:
            # Extract the tile in a window
            textureTile = pygame.Surface((self.cellWidth,self.cellHeight),pygame.SRCALPHA)
            textureTile.blit(texture,(0,0),textureRect)
            # Rotate the surface with the tile
            rotatedTile = pygame.transform.rotate(textureTile,tile.angle)
            # Compute the new coordinate on the screen, knowing that we rotate around the center of the tile
            spritePoint.x -= (rotatedTile.get_width() - textureTile.get_width()) // 2
            spritePoint.y -= (rotatedTile.get_height() - textureTile.get_height()) // 2
            # Render the rotatedTile
            window.blit(rotatedTile,spritePoint)

class BackgroundLayer(Layer):
    def __init__(self,ui,gameState,tiles,surfaceFlags=pygame.SRCALPHA):
        super().__init__(ui)
        self.gameState = gameState
        self.layout = tiles
        self.surfaceFlags = surfaceFlags
    
    def renderBoard(self,window):
        pygame.draw.rect(window,(50,50,50),self.gameState.boardRect)
        for x in range(0,int(self.gameState.boardSize.y)+1,int(self.gameState.cellSize.x)):
            pygame.draw.line(window, (70,0,70),(x+self.gameState.boardPosition.x,self.gameState.boardPosition.y),(x+self.gameState.boardPosition.x,self.gameState.boardPosition.y+self.gameState.boardSize.y))
            pygame.draw.line(window, (70,0,70),(self.gameState.boardPosition.x,self.gameState.boardPosition.y+x),(self.gameState.boardPosition.x+self.gameState.boardSize.x,self.gameState.boardPosition.y+x))

    def renderFrame(self,window):
        for tile in self.layout:
            ####################### here for the if statement that determines the tile isn't where a Sliding Door will go #########################
            self.renderTile(window,tile)

    def render(self, window):
        self.renderBoard(window)
        self.renderFrame(window)

class TileLayer(Layer):
    def __init__()

class ForegroundLayer(Layer):  
    def __init__(self,ui,gameState,tiles,surfaceFlags=pygame.SRCALPHA):
        super().__init__(ui)
        self.gameState = gameState
        self.surfaceFlags = surfaceFlags
        self.tiles = tiles
    
    def render(self,window):
        for tile in self.tiles:
            self.renderTile(window,tile)
            
    def update(self):
        for tile in self.tiles:
            AnimateTile.run(tile)


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

class menu(GameMode):
    def __init__(self, ui):
        self.ui = ui
        self.mainMenu = pygame_menu.Menu('Main Menu', 450, 400, theme=themes.THEME_SOLARIZED)
        self.mainMenu.add.button('Resume Game', self.start_the_game)
        self.mainMenu.add.button('Daily Challenge', self.daily_level_menu)
        self.mainMenu.add.button('Start a New Game', self.start_level_menu)
        self.mainMenu.add.button('Settings', self.settings_menu)
        self.mainMenu.add.button('Quit', pygame_menu.events.EXIT)
        
        self.dailyLevelMenu = pygame_menu.Menu('Daily Challenge', 450, 400, theme=themes.THEME_BLUE)
        self.dailyLevelMenu.add.selector('Difficulty :', [('Normal', 5), ('Hard', 6), ('Hardest', 7)], onchange=self.setDifficulty)
        self.dailyLevelMenu.add.button('Play', self.start_the_game)
        
        self.startLevelMenu = pygame_menu.Menu('New Game', 450, 400, theme=themes.THEME_BLUE)
        self.startLevelMenu.add.selector('Difficulty :', [('Easy', 4), ('Normal', 5), ('Hard', 6), ('Hardest', 7)], onchange=self.setDifficulty)
        self.startLevelMenu.add.selector('Collection :', [('Marvel Comics', 'marvel'), ('Pirates', 'pirate'), ('Anime', 'anime'), ('Fantasy', 'fantasy')], onchange=self.setGameCollection)
        self.startLevelMenu.add.selector('Level :', [('01',1),('02',2),('03',3),('04',4),('05',5),('06',6),('07',7)], onchange=self.setGameLevel)
        self.startLevelMenu.add.button('Play', self.start_the_game)
        
        self.settingsMenu = pygame_menu.Menu('Settings', 450, 400, theme=themes.THEME_BLUE)
        self.settingsMenu.add.range_slider(title="Music :", default=7, range_values=(0, 10), increment=1, value_format=lambda x: str(int(x)), onchange=self.setMusicVolume)
        self.settingsMenu.add.range_slider(title="Sound Effects :", default=7, range_values=(0, 10), increment=1, value_format=lambda x: str(int(x)), onchange=self.setSFXVolume)
        self.settingsMenu.add.selector('Theme :', [('Blue', 0), ('Red', 1), ('Yellow', 2), ('Orange', 3), ('Purple', 4)], onchange=self.setTheme)
        
    def processInput(self):
        pass
    
    def update(self):
        self.events = pygame.event.get()
        for event in self.events:
            if event.type == pygame.QUIT:
                exit()
        
    def render(self):
        darkSurface = pygame.Surface(self.ui.surface.get_size(),flags=pygame.SRCALPHA)
        pygame.draw.rect(darkSurface, (0,0,0,150), darkSurface.get_rect())
        self.ui.surface.blit(darkSurface, (0,0))
        if self.mainMenu.is_enabled():
            self.mainMenu.update(self.events)
            self.mainMenu.draw(self.ui.surface)

    def daily_level_menu(self):
        self.mainMenu._open(self.dailyLevelMenu)
            
    def start_level_menu(self):
        self.mainMenu._open(self.startLevelMenu)
    
    def settings_menu(self):
        self.mainMenu._open(self.settingsMenu)
    
    def start_the_game(self):
        self.ui.gameMode = PlayGameMode(self.ui)
 
    def setDifficulty(self, _, difficulty):
        self.ui.cellCount = difficulty

    def setGameCollection(self, value, collection):
        self.ui.collection = collection

    def setGameLevel(self, value, level):
        self.ui.level = level
    
    def setMusicVolume(self, level):
        self.ui.musicVol = level
    
    def setSFXVolume(self, level):
        self.ui.sfxVol = level
    
    def setTheme(self, _, level):
        self.ui.Theme = level
            
class PlayGameMode(GameMode):
    def __init__(self, ui):
        self.ui = ui
        self.bombTile = MoveableAnimatedActionTile(self,"bomb.png",Vector2(0,0),Vector2(0,0),73,animateSpeed=0.09)
        self.bombTile.action = EndCommand(self,self.bombTile)
        self.commands = []
        bomb = copy(self.bombTile)
        self.layers = [
            BackgroundLayer(self.gameState.cellSize,self.gameState.themeImage,self.gameState,self.gameState.frame),
            BoardLayer(self.gameState.cellSize,self.gameState.pictureImage,self.gameState,self.gameState.board),
            InFlightLayer(self.gameState.cellSize,self.gameState.pictureImage,self.gameState,self.gameState.inFlightTiles),
            AnimationLayer(self.gameState.cellSize,self.gameState.themeImage,self.gameState,self.gameState.animatedTiles),
            ForegroundLayer(self.gameState.cellSize,self.gameState.themeImage,self.gameState,self.gameState.newTileButton)
        ]
        
        self.doorPositions = self.gameState.doorPositions
        self.commands = []
        self.mousePosStart = ()
        self.gameOver = False

        self.SetDoors()
        self.NewFrame()
        self.NewTileQueue()
        self.NewBoard()
        
    def processInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.commands.append(Pause(self.gameState))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.commands.append(Pause(self.gameState))
                elif event.key == pygame.K_SPACE:
                    self.commands.append(NewTile(self.gameState))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mousePosStart = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                mousePos = pygame.mouse.get_pos()
                if self.mousePosStart and self.gameState.boardRect.collidepoint(self.mousePosStart):
                    if self.gameState.newTileButtonRect.collidepoint(self.mousePosStart):
                        self.commands.append(NewTile(self.gameState))
                    else:
                        mouseVector = vectorInt((Vector2(self.mousePosStart[0],self.mousePosStart[1])-self.gameState.boardPosition) / self.gameState.cellSize.x)
                        if self.gameState.board[int(mouseVector.x)][int(mouseVector.y)] !=0:
                            moveVector = self.orthagonalVector(self.mousePosStart,mousePos)
                            tile = self.gameState.board[int(mouseVector.x)][int(mouseVector.y)]
                            tile.moveVector = moveVector
                            tile.findEndPosition(self.gameState)
        
    def update(self):
        for command in self.commands:
            command.run()
        self.commands.clear()
        for layer in self.layers:
            layer.update()
    
    def render(self):
        self.ui.surface.fill((255,0,0))
        for layer in self.layers:
            layer.render(self.ui.surface)

    def orthagonalVector(self,mouseStartPos,mouseEndPos):
        moveX = int(mouseEndPos[0]-mouseStartPos[0])
        moveY = int(mouseEndPos[1]-mouseStartPos[1])
        if abs(moveX) > abs(moveY):
            return Vector2(moveX//abs(moveX),0)
        elif abs(moveY) > abs(moveX):
            return Vector2(0,moveY//abs(moveY))
        else:
            return Vector2(0,0)

    

###############################################################################
#                             User Interface                                  #
###############################################################################

class UserInterface():
    def __init__(self):
        # Window
        pygame.init()
        self.surface = pygame.display.set_mode((840,1050))
        pygame.display.set_caption("Pieces to Pictures")
        pygame.display.set_icon(pygame.image.load("icon.png"))
        self.gameMode = menu(self)
        self.cellCount = 5
        self.collection = ''
        self.level = 0
        self.gameState = GameState()
        self.running = True 
        
        self.clock = pygame.time.Clock()

    def run(self):
        while self.running:
            self.gameMode.processInput()
            self.gameMode.update()
            self.gameMode.render()
                
            # Update display
            pygame.display.update()    
            self.clock.tick(60)

ui = UserInterface()
ui.run()

pygame.quit()
