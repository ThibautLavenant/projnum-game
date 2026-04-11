from numpy._typing import NDArray
import pygame
import random
import numpy as np
from models import *

class MainMenuStateModel(ModeStateModel):
    border = 40 #pixels
    spacing = 15 #pixels
    itemWidth = (width- 2*border - 2*spacing) / 3
    itemHeight = (height- 2*border -spacing) / 2
    font = pygame.font.Font("freesansbold.ttf", 12)
    button1: pygame.Rect
    button2: pygame.Rect
    button3: pygame.Rect
    button4: pygame.Rect
    button5: pygame.Rect
    imgPath = [
        "img\\mode1.png",
        "img\\mode2.png",
        "img\\mode3.png",
        "img\\mode4.png",
        "img\\mode5.png",
    ]
    descriptions = [
        "Émission neutronique",
        "Gestion puissance",
        "Fission nucléaire",
        "Barres de contrôle",
        "Réacteur nucléaire",
    ]

    # ====== Helpers ======

    def drawMenuItem(self, x, y, modeNum, screen):
        pygame.draw.rect(screen, blanc,
                    (
                        x,
                        y,
                        self.itemWidth,
                        self.itemHeight,
                    ),
        )
        img = pygame.image.load(self.imgPath[modeNum - 1])
        resized_img = pygame.transform.smoothscale(img, (self.itemWidth - 2 * self.spacing, self.itemHeight/2))
        screen.blit(resized_img, (x + self.spacing, y + self.spacing))
        messageSuface = self.font.render(f"Mode {modeNum}", True, noir)
        messageRect = messageSuface.get_rect(midbottom=(x + self.itemWidth // 2, y + self.itemHeight * 3 // 4))
        screen.blit(messageSuface, messageRect)
        messageSuface = self.font.render(self.descriptions[modeNum - 1], True, noir)
        messageRect = messageSuface.get_rect(midtop=(x + self.itemWidth // 2, y + self.itemHeight * 3 // 4))
        screen.blit(messageSuface, messageRect)

    # ====== Main functions ======

    def prepare(self, screen):
        pygame.display.set_caption("Simulation de réacteur nucléaire")

        # Init clickable areas
        # Mode 1
        x = self.border
        y = self.border
        self.button1 = pygame.Rect(x, y, self.itemWidth, self.itemHeight)

        # Mode 2
        x = self.border + self.spacing + self.itemWidth
        y = self.border
        self.button2 = pygame.Rect(x, y, self.itemWidth, self.itemHeight)

        # Mode 3
        x = self.border + 2*(self.spacing + self.itemWidth)
        y = self.border
        self.button3 = pygame.Rect(x, y, self.itemWidth, self.itemHeight)

        # Mode 4
        x = self.border
        y = self.border + self.spacing + self.itemHeight
        self.button4 = pygame.Rect(x, y, self.itemWidth, self.itemHeight)

        # Mode 5
        x = self.border + self.spacing + self.itemWidth
        y = self.border + self.spacing + self.itemHeight
        self.button5 = pygame.Rect(x, y, self.itemWidth, self.itemHeight)

    def update(self, events, setMode):
        # Set cursor type
        pos = pygame.mouse.get_pos()
        if self.button1.collidepoint(pos) or \
           self.button2.collidepoint(pos) or \
           self.button3.collidepoint(pos) or \
           self.button4.collidepoint(pos) or \
           self.button5.collidepoint(pos) :
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else :
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP1 or event.key == pygame.K_1:
                    setMode(1)
                elif event.key == pygame.K_KP2 or event.key == pygame.K_2:
                    setMode(2)
                elif event.key == pygame.K_KP3 or event.key == pygame.K_3:
                    setMode(3)
                elif event.key == pygame.K_KP4 or event.key == pygame.K_4:
                    setMode(4)
                elif event.key == pygame.K_KP5 or event.key == pygame.K_5:
                    setMode(5)
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button1.collidepoint(pos):
                    setMode(1)
                elif self.button2.collidepoint(pos):
                    setMode(2)
                elif self.button3.collidepoint(pos):
                    setMode(3)
                elif self.button4.collidepoint(pos):
                    setMode(4)
                elif self.button5.collidepoint(pos):
                    setMode(5)


    def paint(self, screen):

        # Mode 1
        x = self.border
        y = self.border
        self.drawMenuItem(x, y, 1, screen)

        # Mode 2
        x = self.border + self.spacing + self.itemWidth
        y = self.border
        self.drawMenuItem(x, y, 2, screen)

        # Mode 3
        x = self.border + 2*(self.spacing + self.itemWidth)
        y = self.border
        self.drawMenuItem(x, y, 3, screen)

        # Mode 4
        x = self.border
        y = self.border + self.spacing + self.itemHeight
        self.drawMenuItem(x, y, 4, screen)

        # Mode 5
        x = self.border + self.spacing + self.itemWidth
        y = self.border + self.spacing + self.itemHeight
        self.drawMenuItem(x, y, 5, screen)

    def export_datas():
        pass
