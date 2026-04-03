import pygame
import random
import numpy as np

pygame.init()
width, height = 800, 600
rightMenuSize = 200
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
fps = 60

noir = (10, 10, 10)
blanc = (245, 245, 245)
violet = (148, 0, 211)

bleu = (50, 100, 255)
jaune = (255, 255, 0)
orange = (255, 165, 0)
rouge = (255, 50, 50)

cell_size = 20 #Taille des cellules
cols, rows = (width - rightMenuSize)//cell_size, height//cell_size
border = 5 #Bordure inter-cellules
JTokWh = 2.77778e-7 #Pour convertir des Joules en kWh

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

rightMenu = RightMenu()
rightMenu.prepare_menu()

pxTom = 10e-2/20 #Facteur de conversion en m/px (permet de passer de px à m, ici 1px = 0.05cm =5e-4m)
CToK = 273.15 #Conversion Celsius-Kelvin
Gamma = 50 #Facteur d'échelle pour les échanges thermiques, ici on prend 1s de simu = Gamma secondes réelles

c_s = cell_size*pxTom #Taille réelle des cellules
v_b = 0.06 #Vitesse réelle des bulles en m/s
beta = int(c_s*fps/(v_b*10)) #Tick pour la remontée des bulles, *10 pour la simu

T0 = CToK + 20 #Température initiale de l'eau = température ambiante donc 25°C
T_ev = CToK + 100 #Température d'évaporation de l'eau (à p ambiante)

rho_eau = 997 #Masse volumique de l'eau en kg/m^3
C_me = 4180 #Capacité thermique massique de l'eau en J/kg
m_eau = rho_eau*(cell_size*pxTom)**3 #Masse d'eau dans une cellule

m_n = 1.6749275e-27 #Masse d'un neutron en kg
Ec_fast = 3e-13 #Énergie cinétique en J des neutrons rapides de l'ordre de 2MeV
Ec_slow = 6e-21 #Énergie cinétique en J des neutrons lents de l'ordre de 0.038eV
nbr_nav = 5 #Nombre de neutrons intéragissant avant évaporation --> pour déterminer le facteur d'adaptation voir ligne suivante
q_ad_slow = m_eau*C_me*(T_ev-T0)/(Ec_slow*nbr_nav) #Facteur d'adaptation pour la simu --> permet de chauffer plus vite par les neutrons thermiques
q_ad_fast = m_eau*C_me*(T_ev-T0)/(Ec_fast*nbr_nav) #Facteur d'adaptation pour la simu --> permet de chauffer plus vite par les neutrons thermiques

p_int_rapide = 10 #Probabilité d'intéraction des neutrons rapides avec l'eau en %
p_abs_lente = 0.1*p_int_rapide #Probabilité d'absorption des neutrons lents en %
p_n0_rapides = 50 #Proportion de neutrons rapides à l'apparition en %

Interval = (T_ev-T0)/4 #Étendue divisé par le nbr d'intervales souhaités
Palier1 = T0+Interval #Premier palier de température ici de 20°C à 40°C
Palier2 = T0+2*Interval #Second palier donc de 40°C à 60°C
Palier3 = T0+3*Interval #Second palier donc de 40°C à 60°C

delta_t = 1/fps #Écart temporel d'une itération à l'autre (en s)
k1 = 2.4e-3*Gamma #Constante pour la loi de Newton - conducto convectif à l'interface supérieure
k2 = 2.4e-5*Gamma #Constante pour la loi de Fourier - conduction au sein du bassin

alpha_p = 50 #Pourcentage de puissance de la pompe
dT_max_p = 0.1 #Nbr de Kelvin retirés chaque seconde dans le cas où alpha = 100
T_min_p = 50+CToK #Température minimale de refroidissement par pompage
eta_p = 0.33 #Rendement typique d'un réacteur à eau pressurisée
dT_p = alpha_p/100*dT_max_p*delta_t*Gamma #Valeur de \Delta T adapté à la simu
E_utile = 0 #Initialisation de l'énergie utile développée par le réacteur

grid = np.zeros((cols, rows, 2)) #Initialisation de la grille, chaque case contient un vecteur (température, temps)
grid[:, :, 0] = T0 #Remplissage des températures

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

neutrons = []
running = True
sim_speed = 1
n_per_sec = 100 #Nombre de neutrons générés chaque seconde

while running:
    screen.fill(noir)
    rightMenu.computeMetrics(neutrons, grid, sim_speed, E_utile)
    rightMenu.display_menu(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                sim_speed += 1
            elif event.key == pygame.K_DOWN:
                sim_speed = max(1, sim_speed-1)


    if pygame.mouse.get_pressed()[0]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for _ in range(n_per_sec//fps) :
            neutrons.append(Neutron(mouse_x, mouse_y)) #On ajoute les neutrons en dessous du curseur

    for _ in range(sim_speed):
        for n in neutrons[:]:
            n.deplacer()

            if n.x < 0 or n.x > width - rightMenuSize or n.y < 0 or n.y > height: #Si le neutron sort de l'écran on le supprime
                neutrons.remove(n)
                continue

            grid_x, grid_y = int(n.x//cell_size), int(n.y//cell_size) #Coordonnées du neutron cible dans la base des cases

            if 0 <= grid_x < cols and 0 <= grid_y < rows: #On verifie que le neutron soit bien dans l'écran
                if grid[grid_x, grid_y, 0] <= T_ev: #Si la case contient de l'eau liquide
                    interact_rapide = random.choices([0, 1], weights=[100-p_int_rapide, p_int_rapide])[0] #On lance les dés pour l'intéraction rapide
                    absorption_lent = random.choices([0, 1], weights=[100-p_abs_lente, p_abs_lente])[0] #Idem pour l'absorption lente

                    if n.isFast and interact_rapide == 1:
                        grid[grid_x, grid_y, 0] += q_ad_fast*(Ec_fast-Ec_slow)/(m_eau*C_me) #Chaleur fournie par le neutron rapide
                        n.v = 1 #Ralentissement du neutron rapide
                        n.actu_vitesse()
                    elif not n.isFast and absorption_lent == 1:
                        grid[grid_x, grid_y, 0] += q_ad_slow*Ec_slow/(m_eau*C_me) #Chaleur fournie par le neutron lent (concrètement négligeable)
                        if n in neutrons:
                            neutrons.remove(n) #Le neutron lent est quant à lui absorbé donc il disparait
                            continue

        T = grid[:, :, 0] #On isole la matrice des températures
        diff = np.zeros_like(T) #On génère une matrice qui contiendra les flux

        diff[:-1, :] += T[1:, :] - T[:-1, :] #Flux vertical du dessous
        diff[1:, :] += T[:-1, :] - T[1:, :] #Flux vertical du dessus
        diff[:, :-1] += T[:, 1:] - T[:, :-1] #Flux horizontal de la droite
        diff[:, 1:] += T[:, :-1] - T[:, 1:] #Flux horizontal de la gauche

        coeff_conduction = min(0.24, k2) #On plafonne à 1/4, la limite de k2 pour 4 voisines
        isEv = (T<T_ev).astype(float) #Ici on renvoie 0 si c'est de la vapeur et 1 si c'est liquide, car conduction que pour le liquide

        grid[:, :, 0] += coeff_conduction*diff*isEv #On met à jour

        mask = (grid[:, :, 0] - dT_p) > T_min_p #On vérifie la condition, on stocke dans un masque bool
        grid[:, :, 0][mask] -= dT_p #On enlève \Delta T quand c'est vérifié
        n_ref = np.sum(mask) #On compte le nombre d'éléments où c'est bon
        E_utile += n_ref*eta_p*m_eau*C_me*dT_p
        
        # Remontée des bulles de vapeur
        for i in range(cols):
            for j in range(rows):
                #mécanisme de refroidissement continu
                if (grid[i, j, 0] > T0 and j == 0):
                    Ti = grid[i, j, 0]
                    grid[i, j, 0] = Ti-k1*(Ti-T0)*delta_t #On fait baisser la température de la case progressivement

                if grid[i, j, 0] >= T_ev: #Si la case contient de la vapeur
                    if (j > 0 and grid[i, j-1, 0] < T_ev):
                        grid[i, j, 1] += 1 #On incrémente le compteur
                        if (grid[i, j, 1] >= beta):
                            tmp = grid[i, j-1, 0]
                            grid[i, j-1, 0] = grid[i, j, 0]
                            grid[i, j, 0] = tmp
                            grid[i, j-1, 1] = 0
                            grid[i, j, 1] = 0
                    else:
                        grid[i, j, 1] = 0

    # Affichage des cases d'eau
    for i in range(cols):
        for j in range(rows):
            if grid[i, j, 0] >= T_ev: #Si la case contient de la vapeur
                color = noir
            else:
                if grid[i, j, 0] < Palier1:
                    color = bleu
                elif grid[i, j, 0] < Palier2:
                    color = jaune                 
                elif grid[i, j, 0] < Palier3:
                    color = orange
                elif grid[i, j, 0] < T_ev:
                    color = rouge
            pygame.draw.rect(screen, color, (i*cell_size, j*cell_size, cell_size-border, cell_size-border))

    # affichage des neutrons
    for n in neutrons[:]:
        n.dessiner(screen)

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
