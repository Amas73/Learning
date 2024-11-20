from time import sleep
import pygame
import pygame_menu
from pygame_menu import themes
 
 
class GameMode():
    def processInput(self):
        raise NotImplementedError()
    def update(self):
        raise NotImplementedError()
    def render(self, window):
        raise NotImplementedError()

class menu(GameMode):
    def __init__(self, ui):
        self.ui = ui
        self.mainMenu = pygame_menu.Menu('Main Menu', 400, 300, theme=themes.THEME_SOLARIZED)
        self.mainMenu.add.button('Resume Game', self.start_the_game)
        self.mainMenu.add.button('Daily Challenge', self.daily_level_menu)
        self.mainMenu.add.button('Start a New Game', self.start_level_menu)
        self.mainMenu.add.button('Settings', self.settings_menu)
        self.mainMenu.add.button('Quit', pygame_menu.events.EXIT)
        
        self.dailyLevelMenu = pygame_menu.Menu('Daily Challenge', 400, 300, theme=themes.THEME_BLUE)
        self.dailyLevelMenu.add.selector('Difficulty :', [('Normal', 5), ('Hard', 6), ('Hardest', 7)], onchange=self.setDifficulty)
        self.dailyLevelMenu.add.button('Play', self.start_the_game)
        
        self.startLevelMenu = pygame_menu.Menu('New Game', 400, 300, theme=themes.THEME_BLUE)
        self.startLevelMenu.add.selector('Difficulty :', [('Easy', 4), ('Normal', 5), ('Hard', 6), ('Hardest', 7)], onchange=self.setDifficulty)
        self.startLevelMenu.add.selector('Collection :', [('Marvel Comics', 'marvel'), ('Pirates', 'pirate'), ('Anime', 'anime'), ('Fantasy', 'fantasy')], onchange=self.setGameCollection)
        self.startLevelMenu.add.selector('Level :', [('01',1),('02',2),('03',3),('04',4),('05',5),('06',6),('07',7)], onchange=self.setGameLevel)
        self.startLevelMenu.add.button('Play', self.start_the_game)
        
        self.settingsMenu = pygame_menu.Menu('Settings', 400, 300, theme=themes.THEME_BLUE)
        self.settingsMenu.add.selector('Music :', [('Off', 0), ('Low', 1), ('Medium', 2), ('High', 3), ('Loud', 4)], onchange=self.setMusicVolume)
        self.settingsMenu.add.selector('Sound Effects :', [('Off', 0), ('Low', 1), ('Medium', 2), ('High', 3), ('Loud', 4)], onchange=self.setSFXVolume)
        self.settingsMenu.add.selector('Theme :', [('Blue', 0), ('Red', 1), ('Yellow', 2), ('Orange', 3), ('Purple', 4)], onchange=self.setTheme)
        
        self.arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size = (10, 15))
        
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
            if (self.mainMenu.get_current().get_selected_widget()):
                self.arrow.draw(self.ui.surface, self.mainMenu.get_current().get_selected_widget())

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
    
    def setMusicVolume(self, _, level):
        self.ui.musicVol = level
    
    def setSFXVolume(self, _, level):
        self.ui.sfxVol = level
    
    def setTheme(self, _, level):
        self.ui.Theme = level


class PlayGameMode(GameMode):
    def __init__(self, ui):
        self.ui = ui

    def processInput(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.ui.gameMode = menu(self.ui)

    def update(self):
        pass
    
    def render(self):
        self.ui.surface.fill((255,0,0))
    


class UserInterface():
    def __init__(self):
        pygame.init()
        self.surface = pygame.display.set_mode((840,1050))
        pygame.display.set_caption("Pieces to Pictures")
        pygame.display.set_icon(pygame.image.load("icon.png"))
        self.menu = menu(self)
        self.gameMode = menu(self)
        self.cellCount = 5
        self.collection = ''
        self.level = 0


    def run(self):
        while True:
            self.gameMode.processInput()
            self.gameMode.update()
            self.gameMode.render()
        
            pygame.display.update()


ui = UserInterface()
ui.run()

# pygame.quit()
