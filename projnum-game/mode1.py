from numpy._typing import NDArray
import random
import pygame
import numpy as np
from models import *
from physics import *
from simpleRandom import *

class RightMenu:
    font = pygame.font.Font("freesansbold.ttf", 10)
    text_surface_list: list[pygame.Surface]
    text_rect_list: list[pygame.Rect]

    sim_speed_val: int = 1

    temp: float
    nbNeutron: int
    vapQuantity: int

    spacing = 15
    # pix
    start = 10
    # pix

    def prepare_menu(self):
        posX = 605
        posY = self.start
        indicatorsList = ["Température moyenne :"
                            , "Nombre de neutrons :"
                            , "Quantité de vapeur :"
                            , "Vitesse simulation :"
        ]
        
        self.text_surface_list = []
        self.text_rect_list = []
        for indicator in indicatorsList:
            self.text_surface_list.append(self.font.render(
                indicator, True, (255, 255, 255)
            ))
            temp_rect = self.text_surface_list[-1].get_rect(topleft=(posX, posY))
            self.text_rect_list.append(temp_rect)
            posY += self.spacing
            
        posY += 100
        messageList = ["Dans ce Mode de jeu, familisarisez"
                     , "vous avec les concepts de base :"
                     , "Les neutrons sont absorbés par l'eau"
                     , "et la réchauffent. La vapeur d'eau"
                     , "n'absorbe pas les neutrons, ils volent"
                     , "librement. La couleur des cellules "
                     , "d'eau montre leur température."
                     , "Essayez de manipuler les neutrons"
                     , "pour observer les effets."
                     , "Dans ce mode simplifié, l'eau est"
                     , "immobile et conduit la chaleur. La"
                     , "vapeur d'eau ne remonte pas à la"
                     , "surface et les neutrons disparaissent"
                     , "de l'enceinte de confinement"
        ]
        for message in messageList:
            self.text_surface_list.append(self.font.render(
                message, True, (255, 255, 255)
            ))
            temp_rect = self.text_surface_list[-1].get_rect(topleft=(posX, posY))
            self.text_rect_list.append(temp_rect)
            posY += self.spacing

        posY += 20
        messageList = [ "Controles"
            , "Clic gauche : Faire apparaitre un neutron"
            , "Flèche haut : Accélérer la simulation"
            , "Flèche bas : Ralentir la simulation"
        ]
        for message in messageList:
            self.text_surface_list.append(self.font.render(
                message, True, (255, 255, 255)
            ))
            temp_rect = self.text_surface_list[-1].get_rect(topleft=(posX, posY))
            self.text_rect_list.append(temp_rect)
            posY += self.spacing

        self.text_surface_list.append(self.font.render(
            "Légende", True, (255, 255, 255)
        ))
        temp_rect = self.text_surface_list[-1].get_rect(topleft=(posX, posY))
        self.text_rect_list.append(temp_rect)
        posY += self.spacing

        posX += 20
        posY += 20
        self.legendStart = posY
        messageList = [ "Neutron lent"
            , "Neutron rapide"
            , "Case d'eau"
        ]
        for message in messageList:
            self.text_surface_list.append(self.font.render(
                message, True, (255, 255, 255)
            ))
            temp_rect = self.text_surface_list[-1].get_rect(topleft=(posX, posY))
            self.text_rect_list.append(temp_rect)
            posY += self.spacing

        self.font.render(
                message, True, (255, 255, 255)
            )

        self.temp = 0
        self.nbNeutron = 0
        self.vapQuantity = 0
        self.sim_speed_val = 1

    def display_menu(self, screen):
        for i in range(len(self.text_surface_list)):
            screen.blit(self.text_surface_list[i], self.text_rect_list[i])
            
        posY = self.legendStart
        pygame.draw.rect(screen, 
                         blanc, 
                         (605, posY, 3, 3))
        posY += self.spacing
        pygame.draw.rect(screen, 
                         violet, 
                         (605, posY, 3, 3))
        posY += self.spacing
        pygame.draw.rect(
            screen,
            bleu,
            (
                605,
                posY,
                cell_size - border,
                cell_size - border,
            ),
        )

        posY = self.start
        # pix
        temp_surface = self.font.render(f"{self.temp:.0f} °K", True, (255, 255, 255))
        temp_rect = temp_surface.get_rect(topright=(790, posY))
        screen.blit(temp_surface, temp_rect)
        posY += self.spacing
        nbNeutron_surface = self.font.render(
            f"{self.nbNeutron:.0f}", True, (255, 255, 255)
        )
        nbNeutron_rect = nbNeutron_surface.get_rect(topright=(790, posY))
        screen.blit(nbNeutron_surface, nbNeutron_rect)
        posY += self.spacing
        vapQuantity_surface = self.font.render(
            f"{self.vapQuantity}", True, (255, 255, 255)
        )
        vapQuantity_rect = vapQuantity_surface.get_rect(topright=(790, posY))
        screen.blit(vapQuantity_surface, vapQuantity_rect)
        posY += self.spacing
        speed_val_surface = self.font.render(
            f"{self.sim_speed_val}", True, (255, 255, 255)
        )
        speed_val_rect = speed_val_surface.get_rect(topright=(790, posY))
        screen.blit(speed_val_surface, speed_val_rect)

    def computeMetrics(self, neutrons, grid, current_speed):
        self.nbNeutron = neutrons.nb_neutron
        self.temp = np.mean(grid[:, :, 0])
        self.vapQuantity = np.sum(grid[:, :, 0] >= T_ev)
        self.sim_speed_val = current_speed

class Mode1StateModel(ModeStateModel):
    rightMenu: RightMenu
    grid: NDArray
    neutrons: Neutrons
    sim_speed: int

    # ====== Main functions ======

    def prepare(self, screen):
        pygame.display.set_caption("Simulation de réacteur nucléaire - Mode 1")
        self.rightMenu = RightMenu()
        self.rightMenu.prepare_menu()
        self.grid = np.zeros(
            (cols, rows, 2)
        )  # Initialisation de la grille, chaque case contient un vecteur (température, temps)
        self.grid[:, :, 0] = T0  # Remplissage des températures
        self.sim_speed = 1
        self.neutrons = Neutrons() #Initialisation de la collection de neutrons

    def update(self, events, setMode):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.sim_speed = min(50, self.sim_speed + 1)
                elif event.key == pygame.K_DOWN:
                    self.sim_speed = max(1, self.sim_speed - 1)

        # Création des neutrons
        if pygame.mouse.get_pressed()[0]:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for _ in range(self.sim_speed):
                # On ajoute les neutrons en dessous du curseur
                self.neutrons.addNeutron(mouse_x, mouse_y)  

        
        for _ in range(self.sim_speed):
            # Déplacement des neutrons
            self.neutrons.deplacer()

            # Intéraction des neutrons avec les cases d'eau
            interactNeutronsWithWater(self.grid[:, :, 0], self.neutrons)

            # Transfert de chaleur entre les cases d'eau
            handleHeatTransfer(self.grid[:, :, 0])

        self.rightMenu.computeMetrics(self.neutrons, self.grid, self.sim_speed)

    def paint(self, screen):
        # Affichage du menu de droite
        self.rightMenu.display_menu(screen)

        # Affichage des cases d'eau
        for i in range(cols):
            for j in range(rows):
                if self.grid[i, j, 0] >= T_ev:  # Si la case contient de la vapeur
                    color = noir
                else:
                    if self.grid[i, j, 0] < Palier1:
                        color = bleu
                    elif self.grid[i, j, 0] < Palier2:
                        color = jaune
                    elif self.grid[i, j, 0] < Palier3:
                        color = orange
                    elif self.grid[i, j, 0] < T_ev:
                        color = rouge
                pygame.draw.rect(
                    screen,
                    color,
                    (
                        i * cell_size,
                        j * cell_size,
                        cell_size - border,
                        cell_size - border,
                    ),
                )

        # affichage des neutrons
        for i in range(self.neutrons.nb_neutron):
            color = violet if self.neutrons.v[i, 2] else blanc
            pygame.draw.rect(screen, 
                             color, 
                             (int(self.neutrons.pos[i, 0]), 
                              int(self.neutrons.pos[i, 1]), 
                              3, 
                              3))
    
    def export_datas(self):
        pass
