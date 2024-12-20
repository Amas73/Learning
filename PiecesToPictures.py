import os
import pygame
from pygame import Rect
from pygame.math import Vector2
from pygame import surfarray
import random
from copy import copy

def vectorInt(vector: Vector2) -> Vector2:
    return Vector2(int(vector.x), int(vector.y))


###############################################################################
#                               Game State                                    #
###############################################################################

class Tile():
    def __init__(self,state,imageFile,tile,position,angle=None,status=None):
        self.state = state
        self.texture = imageFile
        self.textureGrid = tile
        self.position = position
        self.angle = angle
        self.status = status
        self.frame = 0

class AnimatedTile(Tile):
    def __init__(self,state,imageFile,tile,position,maxFrame,animateSpeed=0.2,angle=None,status=None):
        super().__init__(state,imageFile,tile,position,angle,status)
        self.maxFrame = maxFrame
        self.animationSpeed = animateSpeed
        self.imageFile = imageFile

class AnimatedStateTile(AnimatedTile):
    def __init__(self,state,imageFile,tile,position,maxFrame,animateSpeed=0.2,openTime=0.2,closedTime=0.2,status='closed',angle=None):
        super().__init__(state,imageFile,tile,position,maxFrame,animateSpeed,angle,status)
        self.openTime = openTime
        self.closedTime = closedTime
        self.pauseState = 0

class Piece(Tile):
    def __init__(self,state,tile,position,status=None,moveSpeed=0.3,angle=None):
        super().__init__(state,tile,position,angle,status)
        self.endPosition = copy(position)
        self.speed = moveSpeed
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
        self.status = 'inflight'
        self.state.inFlightTiles.append(self)
        self.state.board[int(self.position.x)][int(self.position.y)] = 0

class AnimatedPiece(Piece,AnimatedTile):
    def __init__(self,state,imageFile,tile,position,maxFrame,status=None,moveSpeed=0.3,animateSpeed=0.2,angle=None):
        super().__init__(state,tile,position,status,moveSpeed,angle)
        self.imageFile = imageFile
        self.maxFrame = maxFrame
        self.animationSpeed = animateSpeed

    def commandAction(self):
        pass

class GameLevel():
    def __init__(self):
        self.difficulties = {'Easy': 4, 'Normal': 5, 'Hard': 6, 'Hardest': 7}
        #self.pictureImage = pygame.image.load("pictures\\avengers.jpg")
        #elf.pictureImage = pygame.image.load("pictures\\00004_1872920033_by_crushedmidget_di2p1ng-pre.jpg")
        #self.pictureImage = pygame.image.load("pictures\\red_dwarf_by_pzns_dfwhlom-375w-2x.jpg")
        #self.pictureImage = pygame.image.load("pictures\\anime_sky_by_nataliciosiqueira_dibkrzw-pre.jpg")
        #self.pictureImage = pygame.image.load("pictures\\rendezvous__by_mr_nerb_dic8m91-pre.jpg")
        self.pictureImage = pygame.image.load("pictures\\soviet_cosmos_rockets_in_the_space_to_star_by_sasha_cher312_dicioc0-pre.jpg")
        #self.pictureImage = pygame.image.load("pictures\\space_dragon_by_ollegr_dicw3wa-pre.jpg")
        #self.pictureImage = pygame.image.load("pictures\\stellar_morning_by_queenneeko_dic3ib1-pre.jpg")
        #self.pictureImage = pygame.image.load("pictures\\superman_colors__by_brunocotic_dicj4ou-414w-2x.jpg")
        #self.pictureImage = pygame.image.load("pictures\\autumn_castle_by_warriorkingt22_diar122-pre.jpg")
        #self.pictureImage = pygame.image.load("pictures\\there_is_a_view_of_a_town_at_sunset_by_funyara_di7citc-pre.jpg")
        #self.pictureImage = pygame.image.load("pictures\\watercolor__wide_angle_landscape_scene_of_a_blonde_by_eilalija_dgt2fv0-pre.jpg")
        #self.pictureImage = pygame.image.load("pictures\\do_you_want_to_come_to_my_party__by_kaawiss_di61q3e-pre.jpg")
        #self.pictureImage = pygame.image.load("pictures\\doctor_who_the_star_beast_wall_poster_by_pzns_dgi9jhj-375w-2x.jpg")
        self.doors = [[(-1,3),0.3,50,20],[(5,3),0.3,50,20],[(2,6),0.3,50,20]]
        #random.seed(22)

class ThemeGraphics():
    def __init__(self,cellSize):
        ### Theme image must be 420 pixels height. 3 rows 140 pixels high each:
        #       First row is the 8 (140x140px) tiles of the frame
        #           - one tile for each side & one tile for each corner.
        #       Second row is the "new tile button" image. Must be 140 x 140 pixels.
        #           - can be animated with each frame going across
        #       Third row is for the sliding door animation. Each column across is a frame.
        ###################################################################################
        self.themeTexture = pygame.image.load("frame.png")
        imageSize = Vector2(self.themeTexture.get_size())
        newSize =  imageSize / 140 * cellSize.elementwise()
        self.themeImage = pygame.transform.smoothscale(self.themeTexture, newSize)
        
class GameState(GameLevel):
    def __init__(self):
        self.level = GameLevel()
        self.cellCount = self.level.difficulties[ui.difficulty]
        self.worldSize = Vector2(840,1050)
        size = int(self.worldSize.x/(self.cellCount+2))
        self.cellSize = Vector2(size,size)
        self.boardSize = Vector2(self.cellSize.x*self.cellCount,self.cellSize.y*(self.cellCount+1))
        self.boardPosition = Vector2(1.5*self.cellSize,2.5*self.cellSize)
        self.boardRect = Rect(self.boardPosition,self.boardSize)
        self.pictureSize = Vector2(self.level.pictureImage.get_size())
        self.pictureCellRatios = self.boardSize.elementwise() / self.pictureSize.elementwise()
        self.pictureCellRatio = max(self.pictureCellRatios.x,self.pictureCellRatios.y)
        self.pictureScaled = pygame.transform.smoothscale(self.level.pictureImage, (self.pictureSize.x * self.pictureCellRatio, self.pictureSize.y * self.pictureCellRatio))
        pictureOffset = ((self.pictureSize.elementwise()*self.pictureCellRatio) - (self.cellSize.elementwise()*self.cellCount)).elementwise()//2
        offsetRect = Rect(int(pictureOffset.x), int(pictureOffset.y), self.cellSize.x*self.cellCount, self.cellSize.y*self.cellCount)
        self.pictureImage = self.pictureScaled.subsurface(offsetRect)
        self.bombTile = self.createBombTile()
        
        self.theme = ThemeGraphics(self.cellSize)
        self.themeImage = self.theme.themeImage
        self.newTileButtonRect = Rect(self.boardPosition,self.cellSize)
        
        self.queue = []
        self.board = []
        self.frame = []
        self.doorPositions = []
        self.slidingDoors = []
        self.newTileButton = []
        self.inFlightTiles = []
        self.animatedTiles = []
        self.status = 'in game'
    
    def createBombTile(self):
        tile = Vector2(0,0)
        position = Vector2(0,0)
        maxFrame = 75
        imageFile = "bomb.png"
        status = None
        moveSpeed = 0.3
        animateSpeed = 0.2
        return AnimatedPiece(self,tile,position,imageFile,maxFrame,status,moveSpeed,animateSpeed,angle=None)

    def DoorIsOpen(self,position):
        for door in self.slidingDoors:
            if door.position == position and door.status == 'open':
                return True
        return False


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
            self.state.board[int(self.tile.position.x)][(int(self.tile.position.y))] = self.tile
            self.CheckDoor()
            self.CheckComplete()
    def CheckDoor(self):
        doorPosition = self.tile.position + self.tile.moveVector
        if doorPosition in self.state.doorPositions and self.state.DoorIsOpen(doorPosition):
            self.state.board[int(self.tile.position.x)][(int(self.tile.position.y))] = 0
            self.tile.position = Vector2(0,0)
            self.tile.status = 'queue'
            self.state.queue.append(self.tile)
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

class Pause(Command):
    def __init__ (self,state):
        self.state = state
    def run(self):
        self.state.status = 'pause'

class NewTile(Command):
    def __init__(self,state):
        self.state = state
    def run(self):
        if len(self.state.queue)>0 and self.state.board[1][0] == 0:
            rand = random.randint(0,5)
            if rand == 0:
                tile = copy(self.state.bombTile)
                self.state.animatedTiles.append(tile)
            else:
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

class LoadLevelCommand(Command):
    def __init__(self,gameMode,action):
        self.gameMode = gameMode
        self.action = action
    def run(self):
        # Load game
        
        state = self.gameMode.gameState
        
        # Window
        windowSize = state.worldSize
        self.gameMode.ui.window = pygame.display.set_mode((int(windowSize.x),int(windowSize.y)))
        
        # Resume game
        self.gameMode.gameOver = False


###############################################################################
#                                Rendering                                    #
###############################################################################

class Layer():
    def __init__(self,cellSize,imageFile):
        self.cellSize = cellSize
        self.texture = imageFile
        
    def setTileset(self,cellSize,imageFile):
        self.cellSize = cellSize
        self.texture = imageFile
        
    @property
    def cellWidth(self):
        return int(self.cellSize.x)

    @property
    def cellHeight(self):
        return int(self.cellSize.y)        
    
    def renderTile(self,window,tile):
        spritePoint = tile.position.elementwise()*self.gameState.cellSize + self.gameState.boardPosition
        texturePoint = vectorInt(tile.textureGrid + Vector2(tile.frame,0)).elementwise()*self.cellSize
        textureRect = Rect(int(texturePoint.x), int(texturePoint.y), self.cellWidth, self.cellHeight)
        if tile.angle is None:
            window.blit(tile.texture,spritePoint,textureRect)
        else:
            # Extract the tile in a window
            textureTile = pygame.Surface((self.cellWidth,self.cellHeight),pygame.SRCALPHA)
            textureTile.blit(tile.texture,(0,0),textureRect)
            # Rotate the surface with the tile
            rotatedTile = pygame.transform.rotate(textureTile,tile.angle)
            # Compute the new coordinate on the screen, knowing that we rotate around the center of the tile
            spritePoint.x -= (rotatedTile.get_width() - textureTile.get_width()) // 2
            spritePoint.y -= (rotatedTile.get_height() - textureTile.get_height()) // 2
            # Render the rotatedTile
            window.blit(rotatedTile,spritePoint)

    def render(self,window):
        raise NotImplementedError() 

class BackgroundLayer(Layer):
    def __init__(self,ui,imageFile,gameState,tiles,surfaceFlags=pygame.SRCALPHA):
        super().__init__(ui,imageFile)
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

class BoardLayer(Layer):  
    def __init__(self,ui,imageFile,gameState,tiles,surfaceFlags=pygame.SRCALPHA):
        super().__init__(ui,imageFile)
        self.gameState = gameState
        self.surfaceFlags = surfaceFlags     
    
    def render(self,window):
        for row in self.gameState.board:
            for tile in row:
                if tile != 0:
                    self.renderTile(window,tile)

class InFlightLayer(Layer):  
    def __init__(self,ui,imageFile,gameState,tiles,surfaceFlags=pygame.SRCALPHA):
        super().__init__(ui,imageFile)
        self.gameState = gameState
        self.surfaceFlags = surfaceFlags     
    
    def render(self,window):
        for tile in self.gameState.inFlightTiles:
            self.renderTile(window,tile)                    

class AnimationLayer(Layer):  
    def __init__(self,ui,imageFile,gameState,tiles,surfaceFlags=pygame.SRCALPHA):
        super().__init__(ui,imageFile)
        self.gameState = gameState
        self.surfaceFlags = surfaceFlags
        self.animatedTiles = tiles
    
    def render(self,window):
        for tile in self.animatedTiles:
            self.renderTile(window,tile)
            if hasattr(tile,"pauseState") and tile.pauseState > 0:
                tile.pauseState -= 1
                if tile.pauseState <= 0:
                    tile.animationSpeed *= -1
                    if tile.status == 'open':
                        tile.status = 'closed'
                else:
                    frame = tile.frame + tile.animationSpeed
                    if frame-2 >= tile.maxFrame:
                        tile.status = 'open'
                        tile.pauseState = tile.openTime
                    elif frame <= 0:
                        tile.pauseState = tile.closedTime
                    else:
                        tile.frame = frame
            else:
                frame = tile.frame + tile.animationSpeed

class ForegroundLayer(Layer):  
    def __init__(self,ui,imageFile,gameState,tiles,surfaceFlags=pygame.SRCALPHA):
        super().__init__(ui,imageFile)
        self.gameState = gameState
        self.surfaceFlags = surfaceFlags
        self.foregroundTiles = tiles
    
    def render(self,window):
        for tile in self.foregroundTiles:
            self.renderTile(window,tile)
            


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
        self.titleFont = pygame.font.Font("BD_Cartoon_Shout.ttf", 48)
        self.itemFont = pygame.font.Font("BD_Cartoon_Shout.ttf", 24)
        
        # Menu items
        # self.menuItems = [
        #     {
        #         'title': 'Resume game',
        #         'action': lambda: self.ui.loadLevel("load")
        #     },
        #     {
        #         'title': 'New Game',
        #         'action': lambda: self.ui.loadLevel("new")
        #     },
        #     {
        #         'title': 'Settings',
        #         'action': lambda: self.ui.loadLevel("settings")
        #     },
        #     {
        #         'title': 'Quit',
        #         'action': lambda: self.ui.quitGame()
        #     }
        # ]      
         
        self.menuItems = [
            {
                'title': 'Easy',
                'action': lambda: self.ui.loadLevel('Easy')
            },
            {
                'title': 'Normal',
                'action': lambda: self.ui.loadLevel('Normal')
            },
            {
                'title': 'Hard',
                'action': lambda: self.ui.loadLevel('Hard')
            },
            {
                'title': 'Hardest',
                'action': lambda: self.ui.loadLevel('Hardest')
            },
            {
                'title': 'Back',
                'action': lambda: self.ui.quitGame()
            }
        ]          

        # Compute menu width
        self.menuWidth = 0
        for item in self.menuItems:
            surface = self.itemFont.render(item['title'], True, (200, 0, 0))
            self.menuWidth = max(self.menuWidth, surface.get_width())
            item['surface'] = surface        
        
        self.currentMenuItem = 1
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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mousePos = pygame.mouse.get_pos()
                for x,rect in enumerate(self.menuRects):
                    if rect.collidepoint(mousePos):
                        menuItem = self.menuItems[x]
                try:
                    menuItem['action']()
                except Exception as ex:
                    print(ex)
                    
    def update(self):
        pass
        
    def render(self, window):
        # Initial y
        y = 150
        
        # Title
        surface = self.titleFont.render("Pieces to Pictures", True, (200, 0, 0))
        x = (window.get_width() - surface.get_width()) // 2
        window.blit(surface, (x, y))
        y += 4 * surface.get_height()
        
        # Draw menu items
        x = (window.get_width() - self.menuWidth) // 2
        self.menuRects = []
        for index, item in enumerate(self.menuItems):
            # Item text
            surface = item['surface']
            window.blit(surface, (x, y))
            surfaceRect = surface.get_rect()
            surfaceRect.x += x
            surfaceRect.y += y
            self.menuRects.append(surfaceRect)
            
            # Cursor
            if index == self.currentMenuItem:
                cursorX = x - self.menuCursor.get_width() - 10
                cursorY = y + (surface.get_height() - self.menuCursor.get_height()) // 2
                window.blit(self.menuCursor, (cursorX, cursorY))
                
            y += (220 * surface.get_height()) // 100           
            

class PlayGameMode(GameMode):
    def __init__(self, ui):
        self.ui = ui

        # Game state
        self.gameState = GameState()
        
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
                    
        self.commands.append(RemoveNonInflightTiles(self.gameState.inFlightTiles))

        # If the game is over, all commands creations are disabled
        if self.gameOver:
            return
        
        for tile in self.gameState.inFlightTiles:
            if tile.status == 'inflight':
                self.commands.append(MoveTile(tile,self.gameState))
        
    def update(self):
        for command in self.commands:
            command.run()
        self.commands.clear()
        if self.gameState.status == 'pause':
            self.running = False
            self.gameOver = True
            self.ui.showMessage("PAUSED")
        if self.gameState.status == 'level complete':
            self.running = False
            self.gameOver = True
            self.ui.showMessage("Level Completed")
    
    def NewTileQueue(self):
        for x in range(self.gameState.cellCount):
            for y in range(self.gameState.cellCount):
                unit = Vector2(x,y)
                position = Vector2(0,0)
                self.gameState.queue.append(Piece(self.gameState,unit,position,'queue'))
        random.shuffle(self.gameState.queue)

    def NewBoard(self):
        self.gameState.board = [[0 for x in range(self.gameState.cellCount+1)] for y in range(self.gameState.cellCount)]

    def SetDoors(self):
        ### Identify how many frames for the Sliding Door animation ###
        pixel_array = surfarray.array3d(self.gameState.themeImage)
        width = len(pixel_array)
        cellSize = int(self.gameState.cellSize.x)
        x=0
        if len(pixel_array[0])>(cellSize*2):
            while True:
                empty = True
                if (x*cellSize) < width:
                    for b in range(cellSize):
                        for a in range(cellSize):
                            if pixel_array[(x*cellSize)+a,(cellSize*2)+b].all() != 0:
                                empty = False
                                break
                if empty:
                    break
                else:
                    x += 1
        for door in self.gameState.level.doors:
            pos = Vector2(door[0])
            speed,open,closed = door[1:4]
            if pos.x>2:
                pos.x += self.gameState.cellCount - 5
            if pos.y>3:
                pos.y +=self.gameState.cellCount - 5
            if pos.x == -1:
                dir = 180
            if pos.y == -1:
                dir = 90
            if pos.y == self.gameState.cellCount+1:
                dir = 270
            self.gameState.slidingDoors.append(AnimatedStateTile(self.gameState,Vector2(0,2),pos,x-1,self.gameState.themeImage,speed,open,closed,dir))
            self.gameState.doorPositions.append(pos)
        self.gameState.animatedTiles.extend(self.gameState.slidingDoors)

    def NewFrame(self):
        frameArray = [(-1,-1,4),(self.gameState.cellCount,-1,5),(-1,self.gameState.cellCount+1,7),(self.gameState.cellCount,self.gameState.cellCount+1,6)]
        for x in range(0,self.gameState.cellCount+1):
            if x < self.gameState.cellCount:
                if Vector2(x,-1) not in self.doorPositions:
                    frameArray.append((x,-1,3))
                if Vector2(x,self.gameState.cellCount+1) not in self.doorPositions:
                    frameArray.append((x,self.gameState.cellCount+1,1))
            if Vector2(-1,x) not in self.doorPositions:
                frameArray.append((-1,x,2))
            if Vector2(self.gameState.cellCount,x) not in self.doorPositions:
                frameArray.append((self.gameState.cellCount,x,0))
        
        for x,y,a in frameArray:
            self.gameState.frame.append(Tile(self.gameState,Vector2(a,0),Vector2(x,y)))
        pixel_array = surfarray.array3d(self.gameState.themeImage)
        width = len(pixel_array)
        ### Identify how many frames for the New Tile button animation ###
        x=0
        cellSize = int(self.gameState.cellSize.x)
        while True:
            empty = True
            if (x*cellSize) < width:
                for b in range(cellSize):
                    for a in range(cellSize):
                        if pixel_array[(x*cellSize)+a,cellSize+b].all() != 0:
                            empty = False
                            break
            if empty:
                break
            else:
                x += 1
        self.gameState.newTileButton.append(AnimatedTile(self.gameState,Vector2(0,1),Vector2(0,0),x-1,self.gameState.themeImage))

    def render(self,window):
        for layer in self.layers:
            layer.render(window)


###############################################################################
#                             User Interface                                  #
###############################################################################

class UserInterface():
    def __init__(self):
        # Window
        pygame.init()
        self.window = pygame.display.set_mode((840,1050))
        pygame.display.set_caption("Pieces to Pictures")
        pygame.display.set_icon(pygame.image.load("icon.png"))
        
        # Modes
        self.playGameMode = None
        self.overlayGameMode = MenuGameMode(self)
        self.currentActiveMode = 'Overlay'
        self.difficulty = 'Normal'
        
        # Loop properties
        self.clock = pygame.time.Clock()
        self.running = True     

    def loadLevel(self, action):
        self.difficulty = action
        if self.playGameMode is None:
            self.playGameMode = PlayGameMode(self)
            self.playGameMode.gameOver = False
        try:
            self.playGameMode.update()
            self.currentActiveMode = 'Play'
        except Exception as ex:
            print(ex)
            self.playGameMode = None
            self.showMessage("Level loading failed :-(")
        
    def showGame(self):
        if self.playGameMode is not None:
            self.currentActiveMode = 'Play'

    def showMenu(self):
        self.overlayGameMode = MenuGameMode(self)
        self.currentActiveMode = 'Overlay'
        
    def showMessage(self, message):
        self.overlayGameMode = MessageGameMode(self, message)
        self.currentActiveMode = 'Overlay'
        
    def quitGame(self):
        self.running = False
       
    def run(self):
        while self.running:
            # Inputs and updates are exclusives
            if self.currentActiveMode == 'Overlay':
                self.overlayGameMode.processInput()
                self.overlayGameMode.update()
            elif self.playGameMode is not None:
                self.playGameMode.processInput()
                try:
                    self.playGameMode.update()
                except Exception as ex:
                    print(ex)
                    self.playGameMode = None
                    self.showMessage("Error during the game update...")
                    
            # Render game (if any), and then the overlay (if active)
            if self.playGameMode is not None:
                self.window.fill((0,0,0))
                self.playGameMode.render(self.window)
            else:
                self.window.fill((0,0,0))
            if self.currentActiveMode == 'Overlay':
                darkSurface = pygame.Surface(self.window.get_size(),flags=pygame.SRCALPHA)
                pygame.draw.rect(darkSurface, (0,0,0,150), darkSurface.get_rect())
                self.window.blit(darkSurface, (0,0))
                self.overlayGameMode.render(self.window)
                
            # Update display
            pygame.display.update()    
            self.clock.tick(60)



ui = UserInterface()
ui.run()

pygame.quit()
