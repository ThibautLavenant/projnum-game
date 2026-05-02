from numpy._typing import NDArray
import pygame
import random
import numpy as np
from models import *
from physics import *
from simpleRandom import *

class RightMenu:
    font = pygame.font.Font('freesansbold.ttf', 10);
    text_surface_list: list[pygame.Surface]
    text_rect_list: list[pygame.Rect]

    sim_speed_val: int = 1
    k_val: float
    temp: float;
    nbNeutron: int;
    nbNeutronTotal: int
    vapQuantity: int;
    enprod: float;
    C_comb: int;
    
    spacing = 15; #pix
    start = 10; #pix
    startX = 605; #pix

    def prepare_menu(self):
        posX = self.startX
        posY = self.start
        indicatorsList = [  #"Température moyenne :"
                             "Nombre de neutrons :"
                            #, "Quantité de vapeur :"
                            , "Vitesse simulation :"
                            #, "Énergie produite :"
                            , "Neutrons total :"
                            , "Concentration combustible :"
                            , "Facteur k :"
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
        messageList = ["Dans ce Mode de jeu, on ne peut plus"
                     , "produire de neutrons avec la souris."
                     , "Il faut utiliser le combustible fissible"
                     , "pour contrôler la réaction en chaîne."
                     , "Cette fois les neutrons rapides sont"
                     , "réfléchis par l'enceinte après avoir"
                     , "ralentis. Les neutrons lents s'échapent"
                     , ""
                     , "Le but est de rester entre 400 et 500"
                     , "neutrons en vol pendant au moins 20s."
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
            , "Flèche gauche : Réduire la concentration"
            , "Flèche droite : Augmenter la concentration"
            , "Echap : Revenir au menu"
        ]
        for message in messageList:
            self.text_surface_list.append(self.font.render(
                message, True, (255, 255, 255)
            ))
            temp_rect = self.text_surface_list[-1].get_rect(topleft=(posX, posY))
            self.text_rect_list.append(temp_rect)
            posY += self.spacing

        posY += 20
        self.text_surface_list.append(self.font.render(
            "Légende", True, (255, 255, 255)
        ))
        temp_rect = self.text_surface_list[-1].get_rect(topleft=(posX, posY))
        self.text_rect_list.append(temp_rect)
        posY += self.spacing

        posX += 20
        self.legendStart = posY
        messageList = [ "Neutron lent"
            , "Neutron rapide"
            , "Uranium-235"
            , "Xénon-135"
            , "Autres éléments non fissibles"
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
        self.C_comb = 0
        self.enprod = 0

    def display_menu(self, screen):
        for i in range(len(self.text_surface_list)):
            screen.blit(self.text_surface_list[i], self.text_rect_list[i])
            
        posY = self.legendStart + 5
        pygame.draw.rect(screen, 
                         blanc, 
                         (self.startX, posY, 3, 3))
        posY += self.spacing
        pygame.draw.rect(screen, 
                         violet, 
                         (self.startX, posY, 3, 3))
        
        posY += self.spacing
        pygame.draw.circle(screen,vertUr,(self.startX, posY), int(0.8*cell_size//2))
        posY += self.spacing
        pygame.draw.circle(screen,violetXe,(self.startX, posY), int(0.8*cell_size//2))
        posY += self.spacing
        pygame.draw.circle(screen,grisVi,(self.startX, posY), int(0.8*cell_size//2))
        
        posY = self.start #pix
        # temp_surface = self.font.render(f"{self.temp:.0f} °K", True, (255, 255, 255))
        # temp_rect = temp_surface.get_rect(topright=(790, posY))
        # screen.blit(temp_surface, temp_rect)
        # posY += self.spacing
        nbNeutron_surface = self.font.render(f"{self.nbNeutron:.0f}", True, (255, 255, 255))
        nbNeutron_rect = nbNeutron_surface.get_rect(topright=(790, posY))
        screen.blit(nbNeutron_surface, nbNeutron_rect)
        posY += self.spacing
        # vapQuantity_surface = self.font.render(f"{self.vapQuantity}", True, (255, 255, 255))
        # vapQuantity_rect = vapQuantity_surface.get_rect(topright=(790, posY))
        # screen.blit(vapQuantity_surface, vapQuantity_rect)
        # posY += self.spacing
        speed_val_surface = self.font.render(f"{self.sim_speed_val}", True, (255, 255, 255))
        speed_val_rect = speed_val_surface.get_rect(topright=(790, posY))
        screen.blit(speed_val_surface, speed_val_rect)
        posY += self.spacing
        # enprod_surface = self.font.render(f"{self.enprod*JTokWh:.1f} kWh", True, (255, 255, 255))
        # enprod_rect = enprod_surface.get_rect(topright=(790, posY))
        # screen.blit(enprod_surface, enprod_rect)
        # posY += self.spacing; #pix
        enprod_surface = self.font.render(f"{self.nbNeutronTotal}", True, (255, 255, 255))
        enprod_rect = enprod_surface.get_rect(topright=(790, posY))
        screen.blit(enprod_surface, enprod_rect)
        posY += self.spacing; #pix
        C_comb_surface = self.font.render(f"{self.C_comb}", True, (255, 255, 255))
        C_comb_rect = C_comb_surface.get_rect(topright=(790, posY))
        screen.blit(C_comb_surface, C_comb_rect)
        posY += self.spacing
        k_val_surface = self.font.render(f"{self.k_val:.2f}", True, (255, 255, 255))
        k_val_rect = k_val_surface.get_rect(topright=(790, posY))
        screen.blit(k_val_surface, k_val_rect)

    def computeMetrics(self, neutrons, grid, current_speed, k):
        self.nbNeutron = neutrons.nb_neutron
        self.nbNeutronTotal = neutrons.total_neutrons
        # self.temp = np.mean(grid[:, :, 0])
        # self.vapQuantity = np.sum(grid[:, :, 0] >= T_ev)
        self.sim_speed_val = current_speed
        # self.enprod = enprod
        self.k_val = k

class Mode3StateModel(ModeStateModel):
    rightMenu: RightMenu
    grid: NDArray
    neutrons: Neutrons
    sim_speed: int


    # ===== Helpers =====

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
                self.E_prod_fission*JToMeV, #Énergie libérée convertie (en MeV)
                self.fact_k, #Facteur de multiplication k (AD)
                100*np.count_nonzero(self.grid == UR_235)/self.grid.size #Concentration réelle du combustible en %
            ])

    def export_datas(self):
        if self.data_list: #On regarde si la liste n'est pas vide
            final_array = np.array(self.data_list)
            header = "Temps(s), NeutInside(AD), NeutTherm(AD), IntFission(AD), IntXenon(AD), IntTot(AD), TotNonInt(AD), EFiss(MeV), Fact_k(AD), Ccomb(%)"
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
        self.fact_k = 0 #Initilisation du facteur k
        self.disap_count_k = 0 #Initilisation du compteur de neutrons disparus pour k
        self.fission_count_k = 0 #Initilisation du compteur de fissions pour k
        self.E_prod_fission = 0 #Initilisation de l'énergie produite par fission

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
                    if (self.C_comb >= 15):
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
                    if (self.C_comb >= 10):
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

            removed_neut = self.neutrons.deplacerWithConfinment()
            self.notInteract_count += removed_neut

            # Déplacement des neutrons
            self.notInteract_count += self.neutrons.deplacerWithConfinment() 

            #Intéractions avec les neutrons           
            (fission_count, Xe_abs_count) = interactNeutronsWithUrXe(self.neutrons, self.grid)
            self.fission_count += fission_count
            self.Xe_abs_count += Xe_abs_count

            self.disap_count_k += removed_neut + fission_count + Xe_abs_count
            self.fission_count_k += fission_count

            if self.disap_count_k >= n_k:
                self.fact_k = (self.fission_count_k*neut_gen_fission)/self.disap_count_k
                self.fission_count_k = 0
                self.disap_count_k = 0

            self.E_prod_fission += fission_count*E_lib_fission

        #Enregistrement des données
        self.save_data()

        self.rightMenu.computeMetrics(self.neutrons, self.grid, self.sim_speed, self.fact_k)
        self.rightMenu.C_comb = self.C_comb

    def paint(self, screen):
        # Affichage du menu de droite
        self.rightMenu.display_menu(screen)

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
