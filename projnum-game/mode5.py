from numpy._typing import NDArray
import pygame
import random
import numpy as np
from models import *
from physics import *
from simpleRandom import *

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
    C_surface: pygame.Surface
    C_rect: pygame.Rect
    sim_speed_val: int = 1

    temp: float;
    nbNeutron: int;
    vapQuantity: int;
    C_comb: int;
    
    spacing = 15; #pix
    start = 10; #pix

    def prepare_menu(self):
        posY = self.start; #pix
        self.nbNeutron_surface = self.font.render("Nombre de neutrons :", True, (255, 255, 255))
        self.nbNeutron_rect = self.nbNeutron_surface.get_rect(topleft=(610, posY))
        posY += self.spacing
        self.speed_surface = self.font.render("Vitesse simulation :", True, (255, 255, 255))
        self.speed_rect = self.speed_surface.get_rect(topleft=(610, posY))  
        posY += self.spacing
        self.C_surface = self.font.render("Concentration combustible :", True, (255, 255, 255))
        self.C_rect = self.C_surface.get_rect(topleft=(610, posY))  

        self.nbNeutron = 0;
        self.sim_speed_val = 1
        self.C_comb = 0

    def display_menu(self, screen):
        screen.blit(self.nbNeutron_surface, self.nbNeutron_rect)
        screen.blit(self.speed_surface, self.speed_rect)
        screen.blit(self.C_surface, self.C_rect)
        posY = self.start; #pix
        nbNeutron_surface = self.font.render(f"{self.nbNeutron:.0f}", True, (255, 255, 255))
        nbNeutron_rect = nbNeutron_surface.get_rect(topright=(790, posY))
        screen.blit(nbNeutron_surface, nbNeutron_rect)
        posY += self.spacing
        speed_val_surface = self.font.render(f"{self.sim_speed_val}", True, (255, 255, 255))
        speed_val_rect = speed_val_surface.get_rect(topright=(790, posY))
        screen.blit(speed_val_surface, speed_val_rect)
        posY += self.spacing
        C_comb_surface = self.font.render(f"{self.C_comb}", True, (255, 255, 255))
        C_comb_rect = C_comb_surface.get_rect(topright=(790, posY))
        screen.blit(C_comb_surface, C_comb_rect)

    def computeMetrics(self, neutrons, current_speed):
        self.nbNeutron = neutrons.nb_neutron
        self.sim_speed_val = current_speed

class Mode5StateModel(ModeStateModel):
    rightMenu: RightMenu
    grid: NDArray
    water_grid: NDArray
    neutrons: Neutrons
    sim_speed: int
    res: int
    n_per_sec: int
    E_utile: float
    data_list: list
    fast_interact_count: int
    slow_interact_count: int
    emitted_neutrons_count: int


    # ===== Helpers =====

    def raiseGasBubble(self):
        for i in range(cols):
            for j in range(rows):
                if self.water_grid[i, j, 0] >= T_ev: #Si la case contient de la vapeur
                    if (j > 0 and self.water_grid[i, j-1, 0] < T_ev):
                        self.water_grid[i, j, 1] += 1 #On incrémente le compteur
                        if (self.water_grid[i, j, 1] >= beta):
                            tmp = self.water_grid[i, j-1, 0]
                            self.water_grid[i, j-1, 0] = self.water_grid[i, j, 0]
                            self.water_grid[i, j, 0] = tmp
                            self.water_grid[i, j-1, 1] = 0
                            self.water_grid[i, j, 1] = 0
                    else:
                        self.water_grid[i, j, 1] = 0
    
    def handleHeatTransfer(self):
        handleHeatTransfer(self.water_grid[:, :, 0]) #On gère le transfert de chaleur dans la grille

        mask = (self.water_grid[:, :, 0] - dT_p) > T_min_p #On vérifie la condition, on stocke dans un masque bool
        self.water_grid[:, :, 0][mask] -= dT_p #On enlève \Delta T quand c'est vérifié
        n_ref = np.sum(mask) #On compte le nombre d'éléments où c'est bon
        self.E_utile += n_ref*eta_p*m_eau*C_me*dT_p

    def save_data(self) :
        t_arrondi = (self.sim_time//self.res)*self.res #On arrondit le temps simulé à la résolution voulue

        if not self.data_list or abs(self.data_list[-1][0] - t_arrondi) > 1e-6 : #On veut une liste vide ou attendre qu'on soit à la sec d'après (on regarde si on est assez différent pour cela)
            self.data_list.append([
                t_arrondi, #Le temps actuel (en s)
                self.neutrons_count, #Nombre actuel de neutrons (AD)
                self.nb_thermiques, #Nombre actuel de neutrons thermiques (AD) 
                self.fission_count, #Nombre d'intéractions de fission (AD)
                self.Xe_abs_count, #Nombre d'intéractions avec du Xénon (AD)
                (self.fission_count + self.Xe_abs_count), #Nombre total d'intéractions (AD)
                self.notInteract_count, #Nombre total de neutrons n'ayant pas intéragit (AD)
            ])

    def export_datas(self):
        if self.data_list: #On regarde si la liste n'est pas vide
            final_array = np.array(self.data_list)
            header = "Temps(s), NeutInside(AD), NeutTherm(AD), IntFission(AD), IntXenon(AD), IntTot(AD), TotNonInt(AD)"
            np.savetxt("Datas/sim_data_mode3.txt", final_array, delimiter = ",", header=header, comments='')

    # ====== Main functions ======

    def prepare(self, screen):
        pygame.display.set_caption("Simulation de réacteur nucléaire - Mode 3")
        self.rightMenu = RightMenu()
        self.rightMenu.prepare_menu()

        # Initialisation de la grille, chaque case contient le type d'atome (0=non fissible;1=Ur;2=Xe)
        self.grid = np.zeros((cols, rows))  
        self.C_comb = 10 #Concentration en combustible en %
        n_comb = int(self.grid.size*self.C_comb/100) #Nombre de cases contenant du combustible
        for i in range(n_comb):
            #On place les cases de combustible aléatoirement
            x, y = random.randint(0, cols-1), random.randint(0, rows-1)
            while self.grid[x, y] != NON_FISSIBLE: #Tant que la case n'est pas vide on cherche une autre position
                x, y = random.randint(0, cols-1), random.randint(0, rows-1)
            self.grid[x, y] = UR_235 #On place du combustible à cet emplacement

        self.water_grid = np.zeros(
            (cols, rows, 2)
        )  # Initialisation de la grille, chaque case contient un vecteur (température, temps)
        self.water_grid[:, :, 0] = T0  # Remplissage des températures

        self.sim_speed = 1
        self.sim_time = 0 #Initialisation du chrono de simulation

        self.neutrons = Neutrons() #Initialisation de la collection de neutrons

        self.data_list = [] #Initialisation du tableau de données
        self.res = 0.1 #Résolution temporelle pour l'enregistrement des données (0.1 = décisecondes, 0.01 = centisecondes...)
        self.fission_count = 0 #Initilisation du compteur d'interactions de fission
        self.neutrons_count = 0 #Initilisation du compteur de neutrons
        self.nb_thermiques = 0 #Initilisation du compteur de neutrons thermiques (lents)
        self.notInteract_count = 0 #Initialisation du compteur de neutrons n'ayant pas intéragit
        self.Xe_abs_count = 0 #Initialisation du compteur de neutrons absorbés par le Xénon
        self.E_utile = 0 #Initialisation de l'énergie utile développée par le réacteur 
        
    def update(self, events, setMode):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.sim_speed = min(50, self.sim_speed + 1)
                elif event.key == pygame.K_DOWN:
                    self.sim_speed = max(1, self.sim_speed - 1)
                elif self.neutrons.nb_neutron == 0 and event.key == pygame.K_RETURN:
                    #On prend les indices de la grille de combustible initiale
                    coord_x, coord_y = np.where(self.grid == UR_235)
                    #On cherche la 1ère cellule la plus à gauche
                    idx_min = np.argmin(coord_x) 
                    target_x = coord_x[idx_min]
                    target_y = coord_y[idx_min]
                    #On convertit en coordonnées (x,y)
                    pos_neut_init = cellTocoord(target_x, target_y, 0) 
                    #On envoit le neutron d'allumage dessus
                    self.neutrons.addNeutron(pos_neut_init[0], pos_neut_init[1]) 
                elif event.key == pygame.K_LEFT:
                    if self.C_comb == 0:
                        continue
                    # previous n_Comb
                    prev_n_comb = int(self.grid.size*self.C_comb/100)
                    # decrease C_comb
                    if (self.C_comb >= 55):
                        self.C_comb = self.C_comb - 5
                    else :
                        self.C_comb = self.C_comb - 1
                    # diff
                    diff_n_comb = prev_n_comb - int(self.grid.size*self.C_comb/100)
                    for i in range(diff_n_comb):
                        res = np.argwhere(self.grid == UR_235)
                        if (len(res) > 0):
                            rx, ry = res[random.randint(0, len(res)-1)]
                            self.grid[rx, ry] = NON_FISSIBLE
                elif event.key == pygame.K_RIGHT:
                    if self.C_comb == 100:
                        continue
                    # previous n_Comb
                    prev_n_comb = int(self.grid.size*self.C_comb/100)
                    # decrease C_comb
                    if (self.C_comb >= 50):
                        self.C_comb = self.C_comb + 5
                    else :
                        self.C_comb = self.C_comb + 1
                    # diff
                    diff_n_comb = int(self.grid.size*self.C_comb/100) - prev_n_comb
                    for i in range(diff_n_comb):
                        res = np.argwhere(self.grid == NON_FISSIBLE)
                        if (len(res) > 0):
                            rx, ry = res[random.randint(0, len(res)-1)]
                            self.grid[rx, ry] = UR_235

        self.neutrons_count = self.neutrons.nb_neutron
        self.nb_thermiques = sum(1 for n in self.neutrons.v[:,2] if n == True)
        for _ in range(self.sim_speed):
            self.sim_time += delta_t #On incrémente le compteur de temps

            # Déplacement des neutrons
            self.notInteract_count += self.neutrons.deplacerWithConfinment() 
            
            # Intéraction des neutrons avec les cases d'eau
            interactNeutronsWithWater(self.water_grid[:, :, 0], self.neutrons)

            # Transfert de chaleur entre les cases d'eau
            self.handleHeatTransfer()

            # Remontée des bulles de vapeur
            self.raiseGasBubble()

            #Intéractions avec les neutrons           
            (fission_count, Xe_abs_count) = interactNeutronsWithUrXe(self.neutrons, self.grid)
            self.fission_count += fission_count
            self.Xe_abs_count += Xe_abs_count

        #Enregistrement des données
        self.save_data()

        self.rightMenu.computeMetrics(self.neutrons, self.sim_speed)
        self.rightMenu.C_comb = self.C_comb

    def paint(self, screen):

        # Affichage du menu de droite
        self.rightMenu.display_menu(screen)
        
        # Affichage des cases d'eau
        for i in range(cols):
            for j in range(rows):
                if self.water_grid[i, j, 0] >= T_ev:  # Si la case contient de la vapeur
                    color = noir
                else:
                    if self.water_grid[i, j, 0] < Palier1:
                        color = bleu
                    elif self.water_grid[i, j, 0] < Palier2:
                        color = jaune
                    elif self.water_grid[i, j, 0] < Palier3:
                        color = orange
                    elif self.water_grid[i, j, 0] < T_ev:
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

        # Affichage des éléments de la grille
        for i in range(cols):
            for j in range(rows):
                if self.grid[i, j] == 0 or self.grid[i, j] == NON_FISSIBLE:  # Si la case ne contient rien ou est une case de réserve
                    color = grisVi
                else:
                    if self.grid[i, j] == UR_235: #Si Ur
                        color = vertUr
                    elif self.grid[i, j] == XE_135: #Si Xé
                        color = violetXe
                pygame.draw.circle(screen,color,cellTocoord(i, j, 0), int(0.8*cell_size//2))

        # affichage des neutrons
        for i in range(self.neutrons.nb_neutron):
            color = violet if self.neutrons.v[i, 2] else blanc
            pygame.draw.rect(screen, 
                             color, 
                             (int(self.neutrons.pos[i, 0]), 
                              int(self.neutrons.pos[i, 1]), 
                              3, 
                              3))
