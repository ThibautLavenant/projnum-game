import pygame
pygame.init()

from models import *
from mode1 import Mode1StateModel
from mode2 import Mode2StateModel
from mode3 import Mode3StateModel
from mode4 import Mode4StateModel
from mode5 import Mode5StateModel

# Pygame initialisation
rightMenuSize = 200
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Simulation de réacteur nucléaire")
clock = pygame.time.Clock()
running = True

activeModeState: ModeStateModel = None
font = pygame.font.Font("freesansbold.ttf", 12)
messageSuface = font.render("Appuyez sur une touche de 1 à 5 pour choisir un mode", True, blanc)
messageRect = messageSuface.get_rect(center=(width // 2, height // 2))

# Main loop
while running:
    screen.fill(noir)

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            if activeModeState is None:
                running = False
            else:
                activeModeState = None
                pygame.display.set_caption("Simulation de réacteur nucléaire")
    
    
    if activeModeState is None:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP1 or event.key == pygame.K_1:
                    activeModeState = Mode1StateModel()
                if event.key == pygame.K_KP2 or event.key == pygame.K_2:
                    activeModeState = Mode2StateModel()
                if event.key == pygame.K_KP3 or event.key == pygame.K_3:
                    activeModeState = Mode3StateModel()
                if event.key == pygame.K_KP4 or event.key == pygame.K_4:
                    activeModeState = Mode4StateModel()
                if event.key == pygame.K_KP5 or event.key == pygame.K_5:
                    activeModeState = Mode5StateModel()
        if activeModeState is not None:
            activeModeState.prepare(screen)

    if activeModeState is not None:
        activeModeState.update(events)
        activeModeState.paint(screen)
    else :
        screen.blit(messageSuface, messageRect)

    pygame.display.flip()
    clock.tick(fps)
    #TODO : getFPS() and display it on the screen

pygame.quit()