from numpy._typing import NDArray
import pygame
import random
import numpy as np
from models import *
from physics import *

class RightMenu:
    font = pygame.font.Font('freesansbold.ttf', 10)
    text_surface_list: list[pygame.Surface]
    text_rect_list: list[pygame.Rect]

    sim_speed_val: int = 1
    temp: float
    nbNeutron: int
    nbNeutronTotal: int
    vapQuantity: int
    
    spacing = 15; #pix
    start = 10; #pix
    startX = 605; #pix

    def prepare_menu(self):
        posX = self.startX
        posY = self.start
        
        indicatorsList = ["Température moyenne :"
                            , "Nombre de neutrons :"
                            , "Quantité de vapeur :"
                            , "Vitesse simulation :"
                            , "Énergie produite :"
                            , "Neutrons total :"
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
        messageList = ["Dans ce Mode de jeu, le but est de"
                     , "produire de l'énergie en chauffant"
                     , "l'eau par les neutrons."
                     , "Cette fois-ci, les bulles de vapeur"
                     , "remontent à la surface et l'eau est"
                     , "refroidie en permanence."
                     , "Le but est d'ateindre 25kWh avec"
                     , "le moins de neutrons possibles."
                     , "Atention, les neutrons qui s'échapent"
                     , "ne contribuent pas à la production"
                     , "d'énergie"
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
        self.enprod = 0

    def display_menu(self, screen):
        for i in range(len(self.text_surface_list)):
            screen.blit(self.text_surface_list[i], self.text_rect_list[i])
        
        posY = self.legendStart
        pygame.draw.rect(screen, 
                         blanc, 
                         (self.startX, posY, 3, 3))
        posY += self.spacing
        pygame.draw.rect(screen, 
                         violet, 
                         (self.startX, posY, 3, 3))
        posY += self.spacing
        pygame.draw.rect(
            screen,
            bleu,
            (
                self.startX,
                posY,
                cell_size - border,
                cell_size - border,
            ),
        )

        posY = self.start #pix
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
        posY += self.spacing; #pix
        enprod_surface = self.font.render(f"{self.nbNeutronTotal}", True, (255, 255, 255))
        enprod_rect = enprod_surface.get_rect(topright=(790, posY))
        screen.blit(enprod_surface, enprod_rect)

    def computeMetrics(self, neutrons : Neutrons, grid, current_speed, enprod):
        self.nbNeutron = neutrons.nb_neutron
        self.nbNeutronTotal = neutrons.total_neutrons
        self.temp = np.mean(grid[:, :, 0])
        self.vapQuantity = np.sum(grid[:, :, 0] >= T_ev)
        self.sim_speed_val = current_speed
        self.enprod = enprod

class Mode2StateModel(ModeStateModel):
    rightMenu: RightMenu
    grid: NDArray
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
        handleHeatTransfer(self.grid[:, :, 0]) #On gère le transfert de chaleur dans la grille

        mask = (self.grid[:, :, 0] - dT_p) > T_min_p #On vérifie la condition, on stocke dans un masque bool
        self.grid[:, :, 0][mask] -= dT_p #On enlève \Delta T quand c'est vérifié
        n_ref = np.sum(mask) #On compte le nombre d'éléments où c'est bon
        self.E_utile += n_ref*eta_p*m_eau*C_me*dT_p

    def save_data(self) :
        t_arrondi = (self.sim_time//self.res)*self.res #On arrondit le temps simulé à la résolution voulue

        if not self.data_list or abs(self.data_list[-1][0] - t_arrondi) > 1e-6 : #On veut une liste vide ou attendre qu'on soit à la sec d'après (on regarde si on est assez différent pour cela)
            self.data_list.append([
                t_arrondi, #Le temps actuel (en s)
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
            np.savetxt("Datas/sim_data_mode2.txt", final_array, delimiter = ",", header=header, comments='')

    # ====== Main functions ======

    def prepare(self, screen):
        pygame.display.set_caption("Simulation de réacteur nucléaire - Mode 2")
        self.rightMenu = RightMenu()
        self.rightMenu.prepare_menu()

        self.grid = np.zeros(
            (cols, rows, 2)
        )  # Initialisation de la grille, chaque case contient un vecteur (température, temps)
        self.grid[:, :, 0] = T0  # Remplissage des températures

        self.sim_speed = 1
        self.sim_time = 0 #Initialisation du chrono de simulation

        self.neutrons = Neutrons() #Initialisation de la collection de neutrons
        self.n_per_sec = 100 #Nombre de neutrons générés chaque seconde
        self.neutron_acc = 0 #Initialisation de l'accumulateur des fractions de neutrons
        self.rdt_size = 10000 #On initialise la taille du tableau pour notre génération aléatoire
        self.angle_table = np.random.uniform(0, 2*np.pi, self.rdt_size) #On génère notre tableau d'angles aléatoires 
        self.vit_table = np.random.choice([1, 3], size = self.rdt_size, p = [(100-p_n0_rapides)/100, p_n0_rapides/100]) #Idem pour les vitesses
        self.fastint_table = np.random.choice([0, 1], size = self.rdt_size, p = [(100-p_int_rapide)/100, p_int_rapide/100]) #On lance les dés pour l'intéraction rapide
        self.slowint_table = np.random.choice([0, 1], size = self.rdt_size, p = [(100-p_abs_lente)/100, p_abs_lente/100]) #Idem pour l'absorption lente

        self.data_list = [] #Initialisation du tableau de données
        self.res = 0.1 #Résolution temporelle pour l'enregistrement des données (0.1 = décisecondes, 0.01 = centisecondes...)
        self.E_utile = 0 #Initialisation de l'énergie utile développée par le réacteur 
        self.fast_interact_count = 0 #Initilisation du compteur d'intéractions rapides
        self.slow_interact_count = 0 #... lentes
        self.emitted_neutrons_count = 0 #Initilisation du compteur de neutrons émis
        self.notInteract_count = 0 #Initialisation du compteur de neutrons n'ayant pas intéragit

    def update(self, events, setMode):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.sim_speed = min(50, self.sim_speed + 1)
                elif event.key == pygame.K_DOWN:
                    self.sim_speed = max(1, self.sim_speed - 1)

        for _ in range(self.sim_speed):
            self.sim_time += delta_t #On incrémente le compteur de temps
            # Création des neutrons
            if pygame.mouse.get_pressed()[0]:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.neutron_acc += self.n_per_sec*delta_t

                while self.neutron_acc >= 1 : #Tant qu'on a accumulé au moins 1 neutron entier, on le crée
                    self.neutrons.addNeutron(mouse_x, mouse_y)
                    self.emitted_neutrons_count += 1
                    self.neutron_acc -= 1 #On en retire un pour pas le re créer

            # Déplacement des neutrons
            self.notInteract_count += self.neutrons.deplacer()
            
            # Intéraction des neutrons avec les cases d'eau
            interactNeutronsWithWater(self.grid[:, :, 0], self.neutrons)

            # Transfert de chaleur entre les cases d'eau
            self.handleHeatTransfer()

            # Remontée des bulles de vapeur
            self.raiseGasBubble()

            #Enregistrement des données
            self.save_data()

        self.rightMenu.computeMetrics(self.neutrons, self.grid, self.sim_speed, self.E_utile)
        

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
