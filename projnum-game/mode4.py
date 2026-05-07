from numpy._typing import NDArray
import pygame
import numpy as np
from models import *
from physics import *

class RightMenu:
    font = pygame.font.Font("freesansbold.ttf", 10)
    text_surface_list: list[pygame.Surface]
    text_rect_list: list[pygame.Rect]

    sim_speed_val: int = 1
    nbNeutron: int = 0
    timer_val: float = 0
    
    spacing = 15
    start = 10
    startX = 605

    def prepare_menu(self):
        posX = self.startX
        posY = self.start
        indicatorsList = [
            "Nombre de neutrons :",
            "Vitesse simulation :",
            "Neutrons absorbés :",
            "Temps stabilisé (s) :"
        ]
        
        self.text_surface_list = []
        self.text_rect_list = []
        for indicator in indicatorsList:
            self.text_surface_list.append(self.font.render(indicator, True, (255, 255, 255)))
            temp_rect = self.text_surface_list[-1].get_rect(topleft=(posX, posY))
            self.text_rect_list.append(temp_rect)
            posY += self.spacing
            
        posY += 60
        messageList = [
            "Objectif du Mode 4 :",
            "Familiarisez-vous avec les",
            "barres de contrôle en graphite.",
            "Elles absorbent les neutrons",
            "pour empêcher l'emballement.",
            "",
            "Des neutrons sont injectés",
            "en continu par les bords.",
            "L'enceinte est remplie d'eau",
            "pour les thermaliser.",
            "",
            "OBJECTIF :",
            "Maintenez la population entre",
            "200 et 300 neutrons pendant",
            f" {time_to_win} secondes consécutives !"
        ]
        for message in messageList:
            self.text_surface_list.append(self.font.render(message, True, (255, 255, 255)))
            temp_rect = self.text_surface_list[-1].get_rect(topleft=(posX, posY))
            self.text_rect_list.append(temp_rect)
            posY += self.spacing

        posY += 20
        messageList = [
            "Contrôles :",
            "Z (haut) / S (bas) : Bouger la barre",
            "Gauche / Droite : Vitesse Simu",
            "Echap : Revenir au menu"
        ]
        for message in messageList:
            self.text_surface_list.append(self.font.render(message, True, (255, 255, 255)))
            temp_rect = self.text_surface_list[-1].get_rect(topleft=(posX, posY))
            self.text_rect_list.append(temp_rect)
            posY += self.spacing

    def display_menu(self, screen):
        for i in range(len(self.text_surface_list)):
            screen.blit(self.text_surface_list[i], self.text_rect_list[i])

        posY = self.start
        nbNeutron_surface = self.font.render(f"{self.nbNeutron:.0f}", True, (255, 255, 255))
        nbNeutron_rect = nbNeutron_surface.get_rect(topright=(790, posY))
        screen.blit(nbNeutron_surface, nbNeutron_rect)
        posY += self.spacing
        
        speed_val_surface = self.font.render(f"{self.sim_speed_val}", True, (255, 255, 255))
        speed_val_rect = speed_val_surface.get_rect(topright=(790, posY))
        screen.blit(speed_val_surface, speed_val_rect)
        posY += self.spacing

        abs_surface = self.font.render(f"{self.absNeutron}", True, (255, 255, 255))
        abs_rect = abs_surface.get_rect(topright=(790, posY))
        screen.blit(abs_surface, abs_rect)
        posY += self.spacing
        
        #Couleur du timer : Vert si on a gagné, Jaune si on est dans la zone, Rouge sinon
        color_timer = rouge
        if self.timer_val >= time_to_win:
            color_timer = vertUr
        elif self.timer_val > 0:
            color_timer = jaune
            
        timer_surface = self.font.render(f"{self.timer_val:.1f} / {time_to_win}", True, color_timer)
        timer_rect = timer_surface.get_rect(topright=(790, posY))
        screen.blit(timer_surface, timer_rect)

    def computeMetrics(self, neutrons, current_speed, timer, abs_count):
            self.nbNeutron = neutrons.nb_neutron
            self.sim_speed_val = current_speed
            self.timer_val = timer
            self.absNeutron = abs_count

class Mode4StateModel(ModeStateModel):
    rightMenu: RightMenu
    water_grid: NDArray
    neutrons: Neutrons
    sim_speed: int

    # ====== Main functions ======

    def prepare(self, screen):
        pygame.display.set_caption("Simulation de réacteur nucléaire - Mode 4 (Barres de contrôle)")
        self.rightMenu = RightMenu()
        self.rightMenu.prepare_menu()
        
        self.water_grid = np.zeros((cols, rows, 2))
        self.water_grid[:, :, 0] = T0  

        self.neutrons = Neutrons()
        self.sim_speed = 1
            
        #Paramètres de la barre de contrôle
        self.rod_w = cell_size - border
        self.rod_h = height
        self.rod_x = (cols // 2) * cell_size #On la place au milieu de l'écran
        self.rod_y = -height // 2 #On laisse la moitiée sortie au début
        self.abs_count = 0

        #Paramètres des sources de neutrons
        self.n_per_sec = 50 #Neutrons générés par seconde par source
        self.neutron_acc_left = 0
        self.neutron_acc_right = 0
        self.gen_dist = 100
        self.gen_left_dist = self.rod_x - self.gen_dist
        self.gen_right_dist = self.rod_x + self.gen_dist
        
        #Timer de victoire
        self.timer = 0
        self.time_to_win = 20

    def update(self, events, setMode):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.sim_speed = min(50, self.sim_speed + 1)
                elif event.key == pygame.K_LEFT:
                    self.sim_speed = max(1, self.sim_speed - 1)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_z]:
            self.rod_y = max(-self.rod_h, self.rod_y - v_rod) #Ne peut pas sortir plus haut que sa taille
        if keys[pygame.K_s]:
            self.rod_y = min(0, self.rod_y + v_rod) #Ne peut pas descendre plus bas que le fond

        for _ in range(self.sim_speed):
            #Injection des neutrons aux extrémités gauche et droite
            self.neutron_acc_left += self.n_per_sec * delta_t
            self.neutron_acc_right += self.n_per_sec * delta_t

            while self.neutron_acc_left >= 1 :
                self.neutrons.addFastNeutron(self.gen_left_dist, height // 2) #Injecté à gauche
                self.neutron_acc_left -= 1
                
            while self.neutron_acc_right >= 1 :
                self.neutrons.addFastNeutron(self.gen_right_dist, height // 2) #Injecté à droite
                self.neutron_acc_right -= 1

            self.neutrons.deplacerWithConfinment()

            interactNeutronsWithWater(self.water_grid[:, :, 0], self.neutrons)
            
            #Absorption par la barre de contrôle
            rod_rect = pygame.Rect(self.rod_x, self.rod_y, self.rod_w, self.rod_h)
            self.abs_count += interactNeutronsWithControlRod(self.neutrons, rod_rect)

            #Condition de victoire : Maintenir entre 200 et 300 neutrons
            if 200 <= self.neutrons.nb_neutron <= 300:
                self.timer += delta_t
            else:
                self.timer = 0 #On reset si on sort de la zone !

        self.rightMenu.computeMetrics(self.neutrons, self.sim_speed, self.timer, self.abs_count)

    def paint(self, screen):
        self.rightMenu.display_menu(screen)

        for i in range(cols):
            for j in range(rows):
                pygame.draw.rect(screen, bleu, (i * cell_size, j * cell_size, cell_size - border, cell_size - border))

        # Affichage de la barre de contrôle
        rod_rect = pygame.Rect(self.rod_x, self.rod_y, self.rod_w, self.rod_h)
        pygame.draw.rect(screen, grisFonce, rod_rect)

        # Affichage des neutrons
        for i in range(self.neutrons.nb_neutron):
            color = violet if self.neutrons.v[i, 2] else blanc
            pygame.draw.rect(screen, color, (int(self.neutrons.pos[i, 0]), int(self.neutrons.pos[i, 1]), 3, 3))
            
    def export_datas(self):
        pass