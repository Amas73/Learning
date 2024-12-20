import pygame
import pygame_menu
from pygame import Vector2
from pygame import Rect
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

class MoveableAnimatedTile(MoveableTile):
    def __init__(self, imageFile:str, tile:Vector2, position:Vector2, maxFrame:int, angle:int=None, moveSpeed:float=0.3, animateSpeed:float=0.2):
        super().__init__(imageFile,tile,position,angle,moveSpeed)
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
        self.boardPosition = Vector2(1.5*self.cellSize.x,2.5*self.cellSize.y)


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

class SetModeCommand(Command):
    def __init__(self, ui:object, menu:object):
        self.ui = ui
        self.ui.currentGameMode = menu



###############################################################################
#                                Rendering                                    #
###############################################################################

class Layer():
    def __init__(self,cellSize):
        self.cellSize = cellSize
        
    def setTileset(self,cellSize):
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

class MenuMainGameMode(GameMode):
    def __init__(self,ui):
        self.ui = ui

        # Font
        self.titleFont = pygame.font.Font("BD_Cartoon_Shout.ttf", 72)
        self.itemFont = pygame.font.Font("BD_Cartoon_Shout.ttf", 48)
        
        menu = pygame_menu.Menu('Pieces To Pictures', 400, 300, theme=pygame_menu.themes.THEME_BLUE)

        menu.add.button('Daily Challenge', SetModeCommand(self.ui,MenuDailyGameMode()))
        menu.add.button('Start a New Game', SetModeCommand(self.ui,MenuStartGame()))
        menu.add.button('Resume Game', SetModeCommand(self.ui,PlayGameMode()))
        menu.add.button('Settings', SetModeCommand(self.ui,MenuSettingsGameMode()))
        menu.add.button('Quit', pygame_menu.events.EXIT)

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

class MenuDailyGameMode(GameMode):
    def __init__(self,ui):
        self.ui = ui

        # Font
        self.titleFont = pygame.font.Font("BD_Cartoon_Shout.ttf", 72)
        self.itemFont = pygame.font.Font("BD_Cartoon_Shout.ttf", 48)
        
        menu = pygame_menu.Menu('Pieces To Pictures', 400, 300, theme=pygame_menu.themes.THEME_BLUE)

        menu.add.label('Daily Challenge Picture:')

        menu.add.selector('Difficulty :', [('Easy', 1), ('Normal', 2), ('Hard', 3), ('Hardest', 4)], onchange=set_difficulty)
        menu.add.button('Play', SetModeCommand(self.ui,PlayGameMode()))
        menu.add.button('Back', pygame_menu.events.EXIT)

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

class MenuStartGame(GameMode):
    def __init__(self,ui):
        self.ui = ui

        # Font
        self.titleFont = pygame.font.Font("BD_Cartoon_Shout.ttf", 72)
        self.itemFont = pygame.font.Font("BD_Cartoon_Shout.ttf", 48)
        
        menu = pygame_menu.Menu('Pieces To Pictures', 400, 300, theme=pygame_menu.themes.THEME_BLUE)

        menu.add.button('Daily Challenge', SetModeCommand(self.ui,MenuDailyGameMode()))
        menu.add.button('Start a New Game', SetModeCommand(self.ui,MenuStartGame()))
        menu.add.button('Resume Game', SetModeCommand(self.ui,ResumeGame()))
        menu.add.button('Settings', SetModeCommand(self.ui,MenuSettingsGameMode()))
        menu.add.button('Quit', pygame_menu.events.EXIT)

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

class MenuSettingsGameMode(GameMode):
    def __init__(self,ui):
        self.ui = ui

        # Font
        self.titleFont = pygame.font.Font("BD_Cartoon_Shout.ttf", 72)
        self.itemFont = pygame.font.Font("BD_Cartoon_Shout.ttf", 48)
        
        menu = pygame_menu.Menu('Pieces To Pictures', 400, 300, theme=pygame_menu.themes.THEME_BLUE)

        menu.add.button('Daily Challenge', SetModeCommand(self.ui,MenuDailyGameMode()))
        menu.add.button('Start a New Game', SetModeCommand(self.ui,MenuStartGame()))
        menu.add.button('Resume Game', SetModeCommand(self.ui,ResumeGame()))
        menu.add.button('Settings', SetModeCommand(self.ui,MenuSettingsGameMode()))
        menu.add.button('Quit', pygame_menu.events.EXIT)

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

class PlayGameMode(GameMode):
    def __init__(self,ui):
        self.ui = ui




###############################################################################
#                             User Interface                                  #
###############################################################################

class UserInterface():
    def __init__(self):
        # Window
        pygame.init()
        self.window = pygame.display.set_mode((840,1050))
        pygame.display.set_caption("Pieces to Pictures")
        self.gameState = GameState()
        self.running = True 
        self.bombTile = MoveableAnimatedActionTile(self,"bomb.png",Vector2(0,0),Vector2(0,0),73,animateSpeed=0.09)
        self.bombTile.action = EndCommand(self,self.bombTile)
        self.commands = []
        bomb = copy(self.bombTile)
        self.layers = [
            ForegroundLayer(self.gameState.cellSize,self.gameState,[bomb])
        ]
        self.currentGameMode = MenuMainGameMode(self)

        self.clock = pygame.time.Clock()

    def processInput(self):
        # Pygame events (close, keyboard and mouse click)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                break

    def render(self,window):
        for layer in self.layers:
            layer.render(window)
    
    def update(self):
        for command in self.commands:
            command.run()
        self.commands.clear()
        for layer in self.layers:
            layer.update()
            
    def quitGame(self):
        self.running = False
       
    def run(self):
        while self.running:
            self.processInput()
            self.update()
            self.window.fill((0,0,0))
            self.render(self.window)
                
            # Update display
            pygame.display.update()    
            self.clock.tick(60)

ui = UserInterface()
ui.run()

pygame.quit()
