from numpy._typing import NDArray
import pygame
import random
import numpy as np
from models import *
from physics import *

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
        self.nbNeutron_surface = self.font.render("Nombre de neutrons :", True, (255, 255, 255))
        self.nbNeutron_rect = self.nbNeutron_surface.get_rect(topleft=(610, posY))
        posY += self.spacing
        self.speed_surface = self.font.render("Vitesse simulation :", True, (255, 255, 255))
        self.speed_rect = self.speed_surface.get_rect(topleft=(610, posY))  

        self.nbNeutron = 0;
        self.sim_speed_val = 1

    def display_menu(self, screen):
        screen.blit(self.nbNeutron_surface, self.nbNeutron_rect)
        screen.blit(self.speed_surface, self.speed_rect)
        
        posY = self.start; #pix
        nbNeutron_surface = self.font.render(f"{self.nbNeutron:.0f}", True, (255, 255, 255))
        nbNeutron_rect = nbNeutron_surface.get_rect(topright=(790, posY))
        screen.blit(nbNeutron_surface, nbNeutron_rect)
        posY += self.spacing
        speed_val_surface = self.font.render(f"{self.sim_speed_val}", True, (255, 255, 255))
        speed_val_rect = speed_val_surface.get_rect(topright=(790, posY))
        screen.blit(speed_val_surface, speed_val_rect)

    def computeMetrics(self, neutrons, current_speed):
        self.nbNeutron = len(neutrons)
        self.sim_speed_val = current_speed

class Neutron:
    def __init__(self, x, y, angle, v):
        self.x = x
        self.y = y
        self.isFast = True
        self.angle = angle
        self.v = v #Répartition des neutrons rapides et lents
        self.taille = 3
        self.actu_vitesse()
    
    def actu_vitesse(self):
        self.vx = self.v * np.cos(self.angle)
        self.vy = self.v * np.sin(self.angle)
        self.isFast = (self.v == 3)
        self.color = violet if self.isFast else blanc
        
    def deplacer(self):
        self.x += self.vx
        self.y += self.vy

    def dessiner(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.taille)

class Mode3StateModel(ModeStateModel):

    # ===== Helpers =====
    def interactNeutronsWithUrXe(self):
        for n in self.neutrons[:]:
            grid_x, grid_y = int(n.x//cell_size), int(n.y//cell_size) #Coordonnées du neutron cible dans la base des cases

            if 0 <= grid_x < cols and 0 <= grid_y < rows: #On verifie que le neutron soit bien dans l'écran

                if self.grid[grid_x, grid_y] == 1 and not n.isFast: #Si c'est un neutron lent et que la case contient du combustible fissile
                    fission_prob = self.fission_prob_table[self.fission_prob_idx] #On jete les dés pour la fission
                    self.fission_prob_idx = (self.fission_prob_idx + 1)%self.rdt_size

                    if fission_prob == 1: #Si la fission s'effectue

                        conv_Xe_prob = self.conv_Xe_prob_table[self.conv_Xe_prob_idx]
                        self.conv_Xe_prob_idx = (self.conv_Xe_prob_idx+1)%self.rdt_size

                        if conv_Xe_prob == 0 : #Si la conversion en Xénon a échoué
                            self.fission_count +=1 #On incrémente le compteur de fission
                            res = np.argwhere(self.grid == 0.5) #On trouve les (i, j) pour les cases de réserve

                            if len(res) > 0: #On vérifie s'il reste des cases de réserve dispo
                                res_loc_idx = self.res_idx_table[self.res_idx] #On définit un indice local qui se sert dans le tableau des indices mélangés
                                self.res_idx = (self.res_idx+1)%(self.res_idx_table.size)
                                rx, ry = res[res_loc_idx%len(res)] #On extrait aléatoirement les coordonnées d'une réserve dispo
                                self.grid[rx, ry] = 1 #On réinsère du combustible à cet emplacement
                                self.grid[grid_x, grid_y] = 0.5 #La combustible alors consommé devient une réserve

                            if n in self.neutrons:
                                self.neutrons.remove(n)

                            pos_px = cellTocoord(grid_x, grid_y, 0) #On prend la position x,y de la cellule
                            for _ in range(3) : #On émet 3 neutrons rapides avec des directions aléatoires
                                angle = self.angle_table[self.angle_idx]
                                self.angle_idx = (self.angle_idx + 1)%self.rdt_size
                                self.neutrons.append(Neutron(pos_px[0], pos_px[1], angle, v_sim_fast))
                        
                        elif conv_Xe_prob == 1: #Si la conversion en Xénon réussit
                            self.grid[grid_x, grid_y] = 1.5 #La case actuelle devient du Xénon

                            res = np.argwhere(self.grid == 0.5) #On trouve les (i, j) pour les cases de réserve
                            if len(res) > 0: #On vérifie s'il reste des cases de réserve dispo
                                res_loc_idx = self.res_idx_table[self.res_idx] #On définit un indice local qui se sert dans le tableau des indices mélangés
                                self.res_idx = (self.res_idx+1)%(self.res_idx_table.size)
                                rx, ry = res[res_loc_idx%len(res)] #On extrait aléatoirement les coordonnées d'une réserve dispo
                                self.grid[rx, ry] = 1 #On réinsère du combustible à cet emplacement

                            if n in self.neutrons:
                                self.neutrons.remove(n)

                            pos_px = cellTocoord(grid_x, grid_y, 0) #On prend la position x,y de la cellule
                            for _ in range(3) : #On émet 3 neutrons rapides avec des directions aléatoires
                                angle = self.angle_table[self.angle_idx]
                                self.angle_idx = (self.angle_idx + 1)%self.rdt_size
                                self.neutrons.append(Neutron(pos_px[0], pos_px[1], angle, v_sim_fast))

                elif self.grid[grid_x, grid_y] == 1.5 and not n.isFast: #Si la case contient du Xénon et qu'on a un neutron lent
                    Xe_abs_prob = self.Xe_abs_prob_table[self.Xe_abs_prob_idx] #On lance les dés pour l'absorption
                    self.Xe_abs_prob_idx = (self.Xe_abs_prob_idx + 1)%self.rdt_size

                    if Xe_abs_prob == 1: #Si il y a absorption par le Xénon
                        self.Xe_abs_count +=1 #On incrémente le compteur associé
                        self.grid[grid_x, grid_y] = 0.5 #La case devient une réserve
                        if n in self.neutrons:
                            self.neutrons.remove(n)

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

        self.grid = np.zeros(
            (cols, rows)
        )  # Initialisation de la grille, chaque case contient un vecteur (0=vide;1=combustible;1.5=xénon)
        self.C_comb = 10 #Concentration en combustible en %
        self.n_comb = int(self.grid.size*self.C_comb/100) #Nombre de cases contenant du combustible
        self.C_res = 50 #Concentration de réserve en %
        self.n_res = int(self.C_res/100*(self.grid.size-self.n_comb)) #Nombre de cases en réserve pour réinsertion du combustible (ici 10% des cases restantes)
        self.n_tot_com = self.n_comb + self.n_res
        self.rep_init = np.random.choice(self.grid.size, self.n_tot_com, replace = False) #On tire C_comb% de cases dans la maille
        self.grid.flat[self.rep_init[:-self.n_res]] = 1
        self.grid.flat[self.rep_init[-self.n_res:]] = 0.5
        self.res_idx_table = np.random.permutation(np.arange(self.n_res)) #On fait un tableau qui mélange les indices qui localisent les cases de réserve
        self.res_idx = 0

        self.sim_speed = 1
        self.sim_time = 0 #Initialisation du chrono de simulation
        self.init_game = 0

        self.neutrons = []
        self.rdt_size = 10000 #On initialise la taille du tableau pour notre génération aléatoire
        self.angle_table = np.random.uniform(0, 2*np.pi, self.rdt_size) #On génère notre tableau d'angles aléatoires
        self.angle_idx = 0 #On initialise le pointeur pour l'angle
        self.fission_prob_table = np.random.choice([0, 1], size = self.rdt_size, p = [(100-p_fission)/100, p_fission/100]) #Idem pour l'absorption lente
        self.fission_prob_idx = 0
        self.Xe_abs_prob_table = np.random.choice([0, 1], size = self.rdt_size, p = [(100-p_Xe_abs)/100, p_Xe_abs/100]) #Idem pour l'absorption lente
        self.Xe_abs_prob_idx = 0
        self.conv_Xe_prob_table = np.random.choice([0, 1], size = self.rdt_size, p = [(100-p_conv_Xe)/100, p_conv_Xe/100]) #Idem pour la conversion en Xénon
        self.conv_Xe_prob_idx = 0

        self.data_list = [] #Initialisation du tableau de données
        self.res = 0.1 #Résolution temporelle pour l'enregistrement des données (0.1 = décisecondes, 0.01 = centisecondes...)
        self.fission_count = 0 #Initilisation du compteur d'interactions de fission
        self.neutrons_count = 0 #Initilisation du compteur de neutrons
        self.nb_thermiques = 0 #Initilisation du compteur de neutrons thermiques (lents)
        self.notInteract_count = 0 #Initialisation du compteur de neutrons n'ayant pas intéragit
        self.Xe_abs_count = 0 #Initialisation du compteur de neutrons absorbés par le Xénon

    def update(self, events, setMode):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.sim_speed = min(50, self.sim_speed + 1)
                elif event.key == pygame.K_DOWN:
                    self.sim_speed = max(1, self.sim_speed - 1)
                elif self.init_game == 0 and event.key == pygame.K_RETURN:
                    coord_x, coord_y = np.where(self.grid == 1) #On prend les indices de la grille de combustible initiale
                    idx_min = np.argmin(coord_x) #On cherche la 1ère cellule la plus à gauche
                    target_x = coord_x[idx_min]
                    target_y = coord_y[idx_min]
                    pos_neut_init = cellTocoord(target_x, target_y, 0) #On convertit en coordonnées (x,y)
                    self.neutrons.append(Neutron(pos_neut_init[0], pos_neut_init[1], 0, v_sim_slow)) #On envoit le neutron d'allumage dessus
                    self.init_game = 1

        for _ in range(self.sim_speed):
            self.neutrons_count = len(self.neutrons)
            self.nb_thermiques = sum(1 for n in self.neutrons if not n.isFast)
            self.sim_time += delta_t #On incrémente le compteur de temps

            # Déplacement des neutrons
            for n in self.neutrons[:]:
                n.deplacer()

                if (n.y < 0 or n.y > height): # Si le neutron sort de l'écran verticalement on le supprime
                    self.neutrons.remove(n)
                    self.notInteract_count += 1
                    
                elif n.x < 0: #S'il sort à gauche il est ralentit et rebondit
                    n.x = 0 #On place bien le neutron sur le bord gauche
                    n.v = v_sim_slow #On le ralentit
                    n.actu_vitesse() #On actualise
                    n.vx = abs(n.vx) #On force sa composante x vers la droite
                elif n.x > width - rightMenuSize: #Pareil à droite
                    n.x = width - rightMenuSize #On place bien le neutron sur le bord droit
                    n.v = v_sim_slow #On le ralentit
                    n.actu_vitesse() #On actualise
                    n.vx = -abs(n.vx) #On force sa composante x vers la gauche

            #Intéractions avec les neutrons           
            self.interactNeutronsWithUrXe()
            #Enregistrement des données
            self.save_data()      

        self.rightMenu.computeMetrics(self.neutrons, self.sim_speed)

    def paint(self, screen):
        # Affichage du menu de droite
        self.rightMenu.display_menu(screen)

        # Affichage des cases d'eau
        for i in range(cols):
            for j in range(rows):
                if self.grid[i, j] == 0 or self.grid[i, j] == 0.5:  # Si la case ne contient rien ou est une case de réserve
                    color = grisVi
                else:
                    if self.grid[i, j] == 1: #Si Ur
                        color = vertUr
                    elif self.grid[i, j] == 1.5: #Si Xé
                        color = violetXe
                pygame.draw.circle(screen,color,cellTocoord(i, j, 0), int(0.8*cell_size//2))

        # affichage des neutrons
        for n in self.neutrons[:]:
            n.dessiner(screen)
