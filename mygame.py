import os
import pygame
from pygame import Rect
from pygame.math import Vector2

os.environ['SDL_VIDEO_CENTERED'] = '1'

class piece():
    def __init__(self,state,position,tile):
        self.state = state
        self.position = position
        self.tile = tile
    def move(self,moveVector):
        pass 

class Tile(piece):
    def move(self,moveVector):
        # Compute new tank position
        newTilePos = self.position + moveVector

        # Don't allow positions outside the world
        if newTilePos.x < 0 or newTilePos.x >= self.state.worldWidth \
        or newTilePos.y < 0 or newTilePos.y >= self.state.worldHeight:
            return

        # Don't allow tower positions 
        for tile in self.state.pieces:
            if newTilePos == tile.position:
                return

        self.position = newTilePos


class GameState():
    def __init__(self):
        self.worldSize = Vector2(10,14)
        self.boardFrame = [ ] #arrays for the setup of the board frame
        self.pieces = [
            Tile(self,Vector2(5,4),Vector2(1,0))
        ]
    
    @property
    def worldWidth(self):
        return int(self.worldSize.x)
    
    @property
    def worldHeight(self):
        return int(self.worldSize.y)
        
    def update(self,moveTileCommand):
        self.pieces[0].move(moveTileCommand)

class UserInterface():
    def __init__(self):
        pygame.init()

        # Game state
        self.gameState = GameState()

        # Rendering properties
        self.cellSize = Vector2(64,64)
        self.pieceTexture = pygame.image.load("avengers.jpg")
        
        # Window
        windowSize = self.gameState.worldSize.elementwise() * self.cellSize
        self.window = pygame.display.set_mode((int(windowSize.x),int(windowSize.y)))
        pygame.display.set_caption("Pieces to Pictures")
        pygame.display.set_icon(pygame.image.load("icon.png"))
        self.moveTileCommand = Vector2(0,0)
        
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
                    
    def update(self):
        self.gameState.update(self.moveTileCommand)
        
    def renderPiece(self,piece):
        # Location on screen
        spritePoint = piece.position.elementwise()*self.cellSize
        
        # Unit texture
        texturePoint = piece.tile.elementwise()*self.cellSize
        textureRect = Rect(int(texturePoint.x), int(texturePoint.y), self.cellWidth, self.cellHeight)
        self.window.blit(self.pieceTexture,spritePoint,textureRect)
        
        # Weapon texure
        texturePoint = Vector2(0,6).elementwise()*self.cellSize
        textureRect = Rect(int(texturePoint.x), int(texturePoint.y), self.cellWidth, self.cellHeight)
        self.window.blit(self.pieceTexture,spritePoint,textureRect)    
        
    def render(self):
        self.window.fill((0,0,0))
        
        # Units
        for tile in self.gameState.pieces:
            self.renderPiece(tile)
        
        pygame.display.update()    
        
    def run(self):
        while self.running:
            self.processInput()
            self.update()
            self.render()
            self.clock.tick(60)



userInterface = UserInterface()
userInterface.run()

pygame.quit()