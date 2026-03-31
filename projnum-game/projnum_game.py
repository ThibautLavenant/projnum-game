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
bleu = (50, 100, 255)
orange = (255, 165, 0)
rouge = (255, 50, 50)

cell_size = 20 #Taille des cellules
cols, rows = (width - rightMenuSize)//cell_size, height//cell_size
border = 5 #Bordure inter-cellules

class RightMenu:
    font = pygame.font.Font('freesansbold.ttf', 12);
    temp_surface: pygame.Surface;
    nbNeutron_surface: pygame.Surface;
    vapQuantity_surface: pygame.Surface;
    temp_rect: pygame.Rect;
    nbNeutron_rect: pygame.Rect;
    vapQuantity_rect: pygame.Rect;

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
        self.temp = 0;
        self.nbNeutron = 0;
        self.vapQuantity = 0;

    def display_menu(self, screen):
        screen.blit(self.temp_surface, self.temp_rect)
        screen.blit(self.nbNeutron_surface, self.nbNeutron_rect)
        screen.blit(self.vapQuantity_surface, self.vapQuantity_rect)
        
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

    def computeMetrics(self, neutrons, grid):
        self.nbNeutron = len(neutrons);
        self.temp = sum([grid[i, j, 0] for i in range(cols) for j in range(rows)])/(cols*rows);
        self.vapQuantity = sum([1 for i in range(cols) for j in range(rows) if grid[i, j, 0] >= T_ev]);

rightMenu = RightMenu();
rightMenu.prepare_menu();

pxTom = 10e-2/20 #Facteur de conversion en m/px (permet de passer de px à m, ici 1px = 0.05cm =5e-4m)
CToK = 273.15 #Conversion Celsius-Kelvin
Gamma = 10 #Facteur d'échelle pour les échanges thermiques, ici on prend 1s de simu = 10s réelles

T0 = CToK + 25 #Température initiale de l'eau = température ambiante donc 25°C
T_ev = CToK + 100 #Température d'évaporation de l'eau (à p ambiante)

rho_eau = 997 #Masse volumique de l'eau en kg/m^3
C_me = 4180 #Capacité thermique massique de l'eau en J/kg
m_eau = rho_eau*(cell_size*pxTom)**3 #Masse d'eau dans une cellule

m_n = 1.6749275e-27 #Masse d'un neutron en kg
Ec_fast = 3e-13 #Énergie cinétique en J des neutrons rapides de l'ordre de 2MeV
Ec_slow = 4e-21 #Énergie cinétique en J des neutrons lents de l'ordre de 0.025eV
nbr_nav = 5 #Nombre de neutrons lents à absorber avant évaporation --> pour déterminer le facteur d'adaptation voir ligne suivante
q_ad = m_eau*C_me*(T_ev-T0)/(Ec_slow*nbr_nav) #Facteur d'adaptation pour la simu --> permet de chauffer plus vite par les neutrons

p_abs_lente = 15 #Probabilité d'absorption des neutrons lents en %
p_int_rapide = 0 #Probabilité d'intéraction des neutrons rapides avec l'eau en %
p_n0_rapides = 50 #Proportion de neutrons rapides à l'apparition en %

Palier1 = T0+(T_ev-T0)/3 #Premier palier de température ici de 25°C à 50°C
Palier2 = T0+2*(T_ev-T0)/3 #Second palier donc de 50°C à 75°C

delta_t = 1/fps #Écart temporel d'une itération à l'autre (en s)
k1 = 2.4e-3*Gamma #Constante pour la loi de Newton - conducto convectif à l'interface supérieure
k2 = 2.4e-5*Gamma #Constante pour la loi de Fourier - conduction au sein du bassin

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
        
    def deplacer(self):
        self.x += self.vx
        self.y += self.vy

    def dessiner(self, surface):
        pygame.draw.circle(surface, blanc, (int(self.x), int(self.y)), self.taille)

neutrons = []
running = True

while running:
    screen.fill(noir)
    rightMenu.computeMetrics(neutrons, grid)
    rightMenu.display_menu(screen)



    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.mouse.get_pressed()[0]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        neutrons.append(Neutron(mouse_x, mouse_y)) #On ajoute les neutrons en dessous du curseur

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
                    grid[grid_x, grid_y, 0] += q_ad*(Ec_fast-Ec_slow)/(m_eau*C_me) #Chaleur fournie par le neutron rapide
                    n.v = 1 #Ralentissement du neutron rapide
                    n.actu_vitesse()
                elif not n.isFast and absorption_lent == 1:
                    grid[grid_x, grid_y, 0] += q_ad*Ec_slow/(m_eau*C_me) #Chaleur fournie par le neutron lent (concrètement négligeable)
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
                    if (grid[i, j, 1] >= 10):
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
