import pygame
import random
import numpy as np

pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
fps = 60

noir = (10, 10, 10)
blanc = (245, 245, 245)
bleu = (50, 100, 255)
orange = (255, 165, 0)
rouge = (255, 50, 50)

cell_size = 20 #Taille des cellules
cols, rows = width//cell_size, height//cell_size
border = 5 #Bordure inter-cellules

T0 = 298.15 #Température initiale de l'eau = température ambiante donc 25°C
T_ev = T0+100 #Température d'évaporation de l'eau (à p ambiante)
m_eau = 0.001 #Masse d'eau dans une cellule ici 1g ce qui correspond à des cellules 3D de 1cm^3 de volume
C_me = 4180 #Capacité thermique massique de l'eau en J/kg
Ec_fast = 3e-13 #Énergie cinétique en J des neutrons rapides de l'ordre de 2MeV
Ec_slow = 4e-21 #Énergie cinétique en J des neutrons lents de l'ordre de 0.025eV
nbr_nav = 5 #Nombre de neutrons rapides à absorber avant évaporation --> pour déterminer le facteur d'adaptation voir ligne suivante
q_ad = m_eau*C_me*(T_ev-T0)/(Ec_fast*nbr_nav) #Facteur d'adaptation pour la simu

p_abs_lente = 1 #Probabilité d'absorption des neutrons lents en %
p_int_rapide = 15 #Probabilité d'intéraction des neutrons rapides avec l'eau en %
p_n0_rapides = 50 #Proportion de neutrons rapides à l'apparition en %

T_reinj = 5 #Temps nécessaire en secondes avant réinjection d'eau à température ambiante
Palier1 = T0+(T_ev-T0)/3 #Premier palier de température ici de 25°C à 50°C
Palier2 = T0+2*(T_ev-T0)/3 #Second palier donc de 50°C à 75°C

grid = [[[T0, 0] for _ in range(rows)] for _ in range(cols)] #Initialisation de la grille, chaque case contient un vecteur (température, temps)

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
        
    def deplacer(self):
        self.x += self.vx
        self.y += self.vy

    def dessiner(self, surface):
        pygame.draw.circle(surface, blanc, (int(self.x), int(self.y)), self.taille)

neutrons = []
running = True
while running:
    screen.fill(noir)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.mouse.get_pressed()[0]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        neutrons.append(Neutron(mouse_x, mouse_y)) #On ajoute les neutrons en dessous du curseur

    for i in range(cols):
        for j in range(rows):
            if grid[i][j][0] >= T_ev: #Si la case contient de la vapeur
                grid[i][j][1] += 1 #On incrémente le compteur
                color = noir
                if grid[i][j][1] > T_reinj*fps: #Si le compteur atteint la valeur fixée
                    grid[i][j][0] = T0 #La température est reset
                    grid[i][j][1] = 0 #Le compteur aussi
            else:
                if grid[i][j][0] < Palier1:
                    color = bleu
                elif grid[i][j][0] < Palier2:
                    color = orange
                elif grid[i][j][0] < T_ev:
                    color = rouge
            pygame.draw.rect(screen, color, (i*cell_size, j*cell_size, cell_size-border, cell_size-border))

    for n in neutrons[:]:
        n.deplacer()
        n.dessiner(screen)

        if n.x < 0 or n.x > width or n.y < 0 or n.y > height: #Si le neutron sort de l'écran on le supprime
            neutrons.remove(n)
            continue

        grid_x, grid_y = int(n.x//cell_size), int(n.y//cell_size) #Coordonnées du neutron cible dans la base des cases

        if 0 <= grid_x < cols and 0 <= grid_y < rows: #On verifie que le neutron soit bien dans l'écran
            if grid[grid_x][grid_y][0] <= T_ev: #Si la case contient de l'eau liquide
                interact_rapide = random.choices([0, 1], weights=[100-p_int_rapide, p_int_rapide])[0] #On lance les dés pour l'intéraction rapide
                absorption_lent = random.choices([0, 1], weights=[100-p_abs_lente, p_abs_lente])[0] #Idem pour l'absorption lente

                if n.isFast and interact_rapide == 1:
                    grid[grid_x][grid_y][0] += q_ad*(Ec_fast-Ec_slow)/(m_eau*C_me) #Chaleur fournie par le neutron rapide
                    n.v = 1 #Ralentissement du neutron rapide
                    n.actu_vitesse()
                elif not n.isFast and absorption_lent == 1:
                    grid[grid_x][grid_y][0] += q_ad*Ec_slow/(m_eau*C_me) #Chaleur fournie par le neutron lent (concrètement négligeable)
                    if n in neutrons:
                        neutrons.remove(n) #Le neutron lent est quant à lui absorbé donc il disparait
                        continue

    pygame.display.flip()
    clock.tick(fps)

pygame.quit()
