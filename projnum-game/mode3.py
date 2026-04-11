from numpy._typing import NDArray
import pygame
import random
import numpy as np
from models import *


class RightMenu:
    font = pygame.font.Font("freesansbold.ttf", 12)
    temp_surface: pygame.Surface
    nbNeutron_surface: pygame.Surface
    vapQuantity_surface: pygame.Surface
    temp_rect: pygame.Rect
    nbNeutron_rect: pygame.Rect
    vapQuantity_rect: pygame.Rect
    speed_surface: pygame.Surface
    speed_rect: pygame.Rect
    sim_speed_val: int = 1

    temp: float
    nbNeutron: int
    vapQuantity: int

    spacing = 15
    # pix
    start = 10
    # pix

    def prepare_menu(self):
        posY = self.start
        # pix
        self.temp_surface = self.font.render(
            "Température moyenne :", True, (255, 255, 255)
        )
        self.temp_rect = self.temp_surface.get_rect(topleft=(610, posY))
        posY += self.spacing
        self.nbNeutron_surface = self.font.render(
            "Nombre de neutrons :", True, (255, 255, 255)
        )
        self.nbNeutron_rect = self.nbNeutron_surface.get_rect(topleft=(610, posY))
        posY += self.spacing
        self.vapQuantity_surface = self.font.render(
            "Quantité de vapeur :", True, (255, 255, 255)
        )
        self.vapQuantity_rect = self.vapQuantity_surface.get_rect(topleft=(610, posY))
        posY += self.spacing
        self.speed_surface = self.font.render(
            "Vitesse simulation :", True, (255, 255, 255)
        )
        self.speed_rect = self.speed_surface.get_rect(topleft=(610, posY))
        self.temp = 0
        self.nbNeutron = 0
        self.vapQuantity = 0
        self.sim_speed_val = 1

    def display_menu(self, screen):
        screen.blit(self.temp_surface, self.temp_rect)
        screen.blit(self.nbNeutron_surface, self.nbNeutron_rect)
        screen.blit(self.vapQuantity_surface, self.vapQuantity_rect)
        screen.blit(self.speed_surface, self.speed_rect)

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
        self.nbNeutron = len(neutrons)
        self.temp = np.mean(grid[:, :, 0])
        self.vapQuantity = np.sum(grid[:, :, 0] >= T_ev)
        self.sim_speed_val = current_speed


class Neutron:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.isFast = True
        self.angle = random.uniform(0, 2 * np.pi)
        self.v = random.choices([1, 3], weights=[100 - p_n0_rapides, p_n0_rapides])[
            0
        ]  # Répartition des neutrons rapides et lents
        self.taille = 3
        self.actu_vitesse()

    def actu_vitesse(self):
        self.vx = self.v * np.cos(self.angle)
        self.vy = self.v * np.sin(self.angle)
        self.isFast = self.v == 3
        self.v_real = (
            (2 * Ec_fast / m_n) ** 0.5 if self.isFast else (2 * Ec_slow / m_n) ** 0.5
        )
        self.color = violet if self.isFast else blanc

    def deplacer(self):
        self.x += self.vx
        self.y += self.vy

    def dessiner(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.taille)


class Mode3StateModel(ModeStateModel):
    rightMenu: RightMenu
    grid: NDArray
    neutrons: NDArray
    sim_speed: int

    # ===== Helpers =====

    # ====== Main functions ======

    def prepare(self, screen):
        pygame.display.set_caption("Simulation de réacteur nucléaire - Mode 3")
        self.rightMenu = RightMenu()
        self.rightMenu.prepare_menu()
        self.grid = np.zeros(
            (cols, rows, 2)
        )  # Initialisation de la grille, chaque case contient un vecteur (température, temps)
        self.grid[:, :, 0] = T0  # Remplissage des températures
        self.neutrons = []
        self.sim_speed = 1

    def update(self, events, setMode):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.sim_speed = min(50, self.sim_speed + 1)
                elif event.key == pygame.K_DOWN:
                    self.sim_speed = max(1, self.sim_speed - 1)

        for _ in range(self.sim_speed):
            # TODO simulation
            continue

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
        for n in self.neutrons[:]:
            n.dessiner(screen)
