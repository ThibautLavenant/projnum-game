from numpy._typing import NDArray
import pygame
import random
import numpy as np
from models import *

class RightMenu:
    font = pygame.font.Font('freesansbold.ttf', 12);
    temp_surface: pygame.Surface;
    nbNeutron_surface: pygame.Surface;
    vapQuantity_surface: pygame.Surface;
    temp_rect: pygame.Rect;
    nbNeutron_rect: pygame.Rect;
    vapQuantity_rect: pygame.Rect;
    speed_surface: pygame.Surface
    speed_rect: pygame.Rect
    sim_speed_val: int = 1

    temp: float;
    nbNeutron: int;
    vapQuantity: int;
    
    spacing = 15; #pix
    start = 10; #pix

    def prepare_menu(self):
        posY = self.start; #pix
        self.temp_surface = self.font.render("Température moyenne :", True, (255, 255, 255))
        self.temp_rect = self.temp_surface.get_rect(topleft=(610, posY))
        posY += self.spacing
        self.nbNeutron_surface = self.font.render("Nombre de neutrons :", True, (255, 255, 255))
        self.nbNeutron_rect = self.nbNeutron_surface.get_rect(topleft=(610, posY))
        posY += self.spacing
        self.vapQuantity_surface = self.font.render("Quantité de vapeur :", True, (255, 255, 255))
        self.vapQuantity_rect = self.vapQuantity_surface.get_rect(topleft=(610, posY))
        posY += self.spacing
        self.speed_surface = self.font.render("Vitesse simulation :", True, (255, 255, 255))
        self.speed_rect = self.speed_surface.get_rect(topleft=(610, posY))

        posY += self.spacing
        self.enprod_surface = self.font.render("Énergie produite :", True, (255, 255, 255))
        self.enprod_rect = self.enprod_surface.get_rect(topleft=(610, posY))       

        self.temp = 0;
        self.nbNeutron = 0;
        self.vapQuantity = 0;
        self.sim_speed_val = 1
        self.enprod = 0

    def display_menu(self, screen):
        screen.blit(self.temp_surface, self.temp_rect)
        screen.blit(self.nbNeutron_surface, self.nbNeutron_rect)
        screen.blit(self.vapQuantity_surface, self.vapQuantity_rect)
        screen.blit(self.speed_surface, self.speed_rect)
        screen.blit(self.enprod_surface, self.enprod_rect)
        
        posY = self.start; #pix
        temp_surface = self.font.render(f"{self.temp:.0f} °K", True, (255, 255, 255))
        temp_rect = temp_surface.get_rect(topright=(790, posY))
        screen.blit(temp_surface, temp_rect)
        posY += self.spacing
        nbNeutron_surface = self.font.render(f"{self.nbNeutron:.0f}", True, (255, 255, 255))
        nbNeutron_rect = nbNeutron_surface.get_rect(topright=(790, posY))
        screen.blit(nbNeutron_surface, nbNeutron_rect)
        posY += self.spacing
        vapQuantity_surface = self.font.render(f"{self.vapQuantity}", True, (255, 255, 255))
        vapQuantity_rect = vapQuantity_surface.get_rect(topright=(790, posY))
        screen.blit(vapQuantity_surface, vapQuantity_rect)
        posY += self.spacing
        speed_val_surface = self.font.render(f"{self.sim_speed_val}", True, (255, 255, 255))
        speed_val_rect = speed_val_surface.get_rect(topright=(790, posY))
        screen.blit(speed_val_surface, speed_val_rect)
        posY += self.spacing; #pix
        enprod_surface = self.font.render(f"{self.enprod*JTokWh:.1f} kWh", True, (255, 255, 255))
        enprod_rect = enprod_surface.get_rect(topright=(790, posY))
        screen.blit(enprod_surface, enprod_rect)

    def computeMetrics(self, neutrons, grid, current_speed, enprod):
        self.nbNeutron = len(neutrons)
        self.temp = np.mean(grid[:, :, 0])
        self.vapQuantity = np.sum(grid[:, :, 0] >= T_ev)
        self.sim_speed_val = current_speed
        self.enprod = enprod

class Neutron:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.isFast = True
        self.angle = random.uniform(0, 2*np.pi)
        self.v = random.choices([1, 3], weights=[100-p_n0_rapides, p_n0_rapides])[0] #Répartition des neutrons rapides et lents
        self.taille = 3
        self.actu_vitesse()
    
    def actu_vitesse(self):
        self.vx = self.v * np.cos(self.angle)
        self.vy = self.v * np.sin(self.angle)
        self.isFast = (self.v == 3)
        self.v_real = (2*Ec_fast/m_n)**0.5 if self.isFast else (2*Ec_slow/m_n)**0.5
        self.color = violet if self.isFast else blanc
        
    def deplacer(self):
        self.x += self.vx
        self.y += self.vy

    def dessiner(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.taille)


class Mode2StateModel(ModeStateModel):
    rightMenu: RightMenu
    grid: NDArray
    neutrons: NDArray
    sim_speed: int
    res: int
    n_per_sec: int
    E_utile: float
    data_list: list
    fast_interact_count: int
    slow_interact_count: int
    emitted_neutrons_count: int

    # ===== Helpers =====
    def interactNeutronsWithWater(self):
        for n in self.neutrons[:]:
            grid_x, grid_y = int(n.x//cell_size), int(n.y//cell_size) #Coordonnées du neutron cible dans la base des cases

            if 0 <= grid_x < cols and 0 <= grid_y < rows: #On verifie que le neutron soit bien dans l'écran
                if self.grid[grid_x, grid_y, 0] <= T_ev: #Si la case contient de l'eau liquide
                    interact_rapide = random.choices([0, 1], weights=[100-p_int_rapide, p_int_rapide])[0] #On lance les dés pour l'intéraction rapide
                    absorption_lent = random.choices([0, 1], weights=[100-p_abs_lente, p_abs_lente])[0] #Idem pour l'absorption lente

                    if n.isFast and interact_rapide == 1:
                        self.fast_interact_count +=1
                        self.grid[grid_x, grid_y, 0] += q_ad_fast*(Ec_fast-Ec_slow)/(m_eau*C_me) #Chaleur fournie par le neutron rapide
                        n.v = 1 #Ralentissement du neutron rapide
                        n.actu_vitesse()
                    elif not n.isFast and absorption_lent == 1:
                        self.slow_interact_count +=1
                        self.grid[grid_x, grid_y, 0] += q_ad_slow*Ec_slow/(m_eau*C_me) #Chaleur fournie par le neutron lent (concrètement négligeable)
                        if n in self.neutrons:
                            self.neutrons.remove(n) #Le neutron lent est quant à lui absorbé donc il disparait
                            continue

    def raiseGasBubble(self):
        for i in range(cols):
            for j in range(rows):
                #mécanisme de refroidissement continu
                if (self.grid[i, j, 0] > T0 and j == 0):
                    Ti = self.grid[i, j, 0]
                    self.grid[i, j, 0] = Ti-k1*(Ti-T0)*delta_t #On fait baisser la température de la case progressivement

                if self.grid[i, j, 0] >= T_ev: #Si la case contient de la vapeur
                    if (j > 0 and self.grid[i, j-1, 0] < T_ev):
                        self.grid[i, j, 1] += 1 #On incrémente le compteur
                        if (self.grid[i, j, 1] >= beta):
                            tmp = self.grid[i, j-1, 0]
                            self.grid[i, j-1, 0] = self.grid[i, j, 0]
                            self.grid[i, j, 0] = tmp
                            self.grid[i, j-1, 1] = 0
                            self.grid[i, j, 1] = 0
                    else:
                        self.grid[i, j, 1] = 0

    def handleHeatTransfer(self):
        T = self.grid[:, :, 0] #On isole la matrice des températures
        diff = np.zeros_like(T) #On génère une matrice qui contiendra les flux

        diff[:-1, :] += T[1:, :] - T[:-1, :] #Flux vertical du dessous
        diff[1:, :] += T[:-1, :] - T[1:, :] #Flux vertical du dessus
        diff[:, :-1] += T[:, 1:] - T[:, :-1] #Flux horizontal de la droite
        diff[:, 1:] += T[:, :-1] - T[:, 1:] #Flux horizontal de la gauche

        coeff_conduction = min(0.24, k2) #On plafonne à 1/4, la limite de k2 pour 4 voisines
        isEv = (T<T_ev).astype(float) #Ici on renvoie 0 si c'est de la vapeur et 1 si c'est liquide, car conduction que pour le liquide

        self.grid[:, :, 0] += coeff_conduction*diff*isEv #On met à jour

        mask = (self.grid[:, :, 0] - dT_p) > T_min_p #On vérifie la condition, on stocke dans un masque bool
        self.grid[:, :, 0][mask] -= dT_p #On enlève \Delta T quand c'est vérifié
        n_ref = np.sum(mask) #On compte le nombre d'éléments où c'est bon
        self.E_utile += n_ref*eta_p*m_eau*C_me*dT_p

    def save_data(self) :
        step = fps//self.res #On calcule le pas de frame correspondant à la résolution souhaitée (<= fps nécessairement)
        t_idx = self.loc_frame_count//step #Compteur entier de pas de temps

        t_act = t_idx / self.res #On calcule le temps actuel en secondes

        if not self.data_list or self.data_list[-1][0] != t_act: #On veut une liste vide ou attendre qu'on soit à la sec d'après
            self.data_list.append([
                t_act, #Le temps actuel (en s)
                np.mean(self.grid[:,:,0]), #La température moyenne actuelle (en K)
                self.E_utile, #L'énergie produite jusqu'à maintenant (en J)
                self.fast_interact_count, #Nombre d'intéractions rapides (AD)
                self.slow_interact_count, #... lentes (AD)
                (self.fast_interact_count + self.slow_interact_count), #Nombre total d'intéractions (AD)
                self.notInteract_count, #Nombre total de neutrons n'ayant pas intéragit
                self.emitted_neutrons_count #Nombre total de neutrons émis
            ])


    def export_datas(self):
        if self.data_list: #On regarde si la liste n'est pas vide
            final_array = np.array(self.data_list)
            header = "Temps(s), Température(K), Énergie (J), IntRapides (AD), IntLentes (AD), IntTot(AD), NeutÉmis (AD)"
            np.savetxt("Datas/sim_data.txt", final_array, delimiter = ",", header=header, comments='')

    # ====== Main functions ======

    def prepare(self, screen):
        pygame.display.set_caption("Simulation de réacteur nucléaire - Mode 2")
        self.rightMenu = RightMenu()
        self.rightMenu.prepare_menu()
        self.grid = np.zeros(
            (cols, rows, 2)
        )  # Initialisation de la grille, chaque case contient un vecteur (température, temps)
        self.grid[:, :, 0] = T0  # Remplissage des températures
        self.neutrons = []
        self.sim_speed = 1
        self.loc_frame_count = 0 #Initialisation du compteur de frame
        self.res = 10 #Résolution temporelle pour l'enregistrement des données (10 = décisecondes, 100 centisecondes...)
        self.n_per_sec = 100 #Nombre de neutrons générés chaque seconde
        self.neutron_acc = 0 #Initialisation de l'accumulateur des fractions de neutrons
        self.E_utile = 0 #Initialisation de l'énergie utile développée par le réacteur
        self.data_list = [] #Initialisation du tableau de données
        self.fast_interact_count = 0 #Initilisation du compteur d'intéractions rapides
        self.slow_interact_count = 0 #... lentes
        self.emitted_neutrons_count = 0 #Initilisation du compteur de neutrons émis
        self.notInteract_count = 0 #Initialisation du compteur de neutrons n'ayant pas intéragit

    def update(self, events):
        self.loc_frame_count += 1 #On incrémente le compteur de frame
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.sim_speed = min(50, self.sim_speed + 1)
                elif event.key == pygame.K_DOWN:
                    self.sim_speed = max(1, self.sim_speed - 1)

        for _ in range(self.sim_speed):
            # Création des neutrons
            if pygame.mouse.get_pressed()[0]:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.neutron_acc += self.n_per_sec / fps

                while self.neutron_acc >= 1 : #Tant qu'on a accumulé au moins 1 neutron entier, on le crée
                    self.neutrons.append(Neutron(mouse_x, mouse_y))
                    self.emitted_neutrons_count += 1
                    self.neutron_acc -= 1 #On en retire un pour pas le re créer

            # Déplacement des neutrons
            for n in self.neutrons[:]:
                n.deplacer()

                if (
                    n.x < 0 or n.x > width - rightMenuSize or n.y < 0 or n.y > height
                ):  # Si le neutron sort de l'écran on le supprime
                    self.neutrons.remove(n)
                    self.notInteract_count += 1
                    continue
            
            # Intéraction des neutrons avec les cases d'eau
            self.interactNeutronsWithWater()

            # Transfert de chaleur entre les cases d'eau
            self.handleHeatTransfer()

            # Remontée des bulles de vapeur
            self.raiseGasBubble()

        self.rightMenu.computeMetrics(self.neutrons, self.grid, self.sim_speed, self.E_utile)
        self.save_data()

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
