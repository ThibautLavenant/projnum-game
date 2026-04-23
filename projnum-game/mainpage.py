import pygame
pygame.init()

from models import *
from mode1 import Mode1StateModel
from mode2 import Mode2StateModel
from mode3 import Mode3StateModel
from mode4 import Mode4StateModel
from mode5 import Mode5StateModel
from mainMenu import MainMenuStateModel

# Pygame initialisation
rightMenuSize = 200
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Simulation de réacteur nucléaire")
clock = pygame.time.Clock()
running = True

activeModeState: ModeStateModel = None
mainMenuMode: ModeStateModel = MainMenuStateModel()
mainMenuMode.prepare(screen)
# font = pygame.font.Font("freesansbold.ttf", 12)
# messageSuface = font.render("Appuyez sur une touche de 1 à 5 pour choisir un mode", True, blanc)
# messageRect = messageSuface.get_rect(center=(width // 2, height // 2))

def setMode(modeNum):
    global activeModeState
    if modeNum == 1:
        activeModeState = Mode1StateModel()
    elif modeNum == 2:
        activeModeState = Mode2StateModel()
    elif modeNum == 3:
        activeModeState = Mode3StateModel()
    # elif modeNum == 4:
    #     activeModeState = Mode4StateModel()
    # elif modeNum == 5:
    #     activeModeState = Mode5StateModel()
    elif modeNum == None:
        activeModeState = None

    if activeModeState is not None:
        activeModeState.prepare(screen)
    return activeModeState

# Main loop
while running:
    screen.fill(noir)

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            if activeModeState is not None:
                activeModeState.export_datas()
                activeModeState = None
                mainMenuMode.prepare(screen)
            else:
                running = False

    if activeModeState is not None:
        activeModeState.update(events, setMode)
        activeModeState.paint(screen)
    else :
        mainMenuMode.update(events, setMode)
        mainMenuMode.paint(screen)  

    pygame.display.flip()
    clock.tick(fps)
    #TODO : getFPS() and display it on the screen

pygame.quit()