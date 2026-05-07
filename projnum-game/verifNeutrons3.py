import pygame
pygame.init()
from numpy._typing import NDArray
import random
import pygame
import numpy as np
import matplotlib.pyplot as plt
from models import *
from physics import *
from simpleRandom import *

# Pygame initialisation
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Vérification simulation neutrons")
clock = pygame.time.Clock()
running = True

def paint(grid, water_grid, neutrons):
    # Affichage des cases d'eau
    for i in range(cols):
        for j in range(rows):
            if water_grid[i, j, 0] >= T_ev:  # Si la case contient de la vapeur
                color = noir
            else:
                if water_grid[i, j, 0] < Palier1:
                    color = bleu
                elif water_grid[i, j, 0] < Palier2:
                    color = jaune
                elif water_grid[i, j, 0] < Palier3:
                    color = orange
                elif water_grid[i, j, 0] < T_ev:
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
            if grid[i, j] == 0 or grid[i, j] == NON_FISSIBLE:  # Si la case ne contient rien ou est une case de réserve
                color = grisVi
            else:
                if grid[i, j] == UR_235: #Si Ur
                    color = vertUr
                elif grid[i, j] == XE_135: #Si Xé
                    color = violetXe
            pygame.draw.circle(screen,color,cellTocoord(i, j, 0), int(0.8*cell_size//2))

    # affichage des neutrons
    for i in range(neutrons.nb_neutron):
        color = violet if neutrons.v[i, 2] else blanc
        pygame.draw.rect(screen, 
                         color, 
                         (int(neutrons.pos[i, 0]), 
                          int(neutrons.pos[i, 1]), 
                          3, 
                          3))

def raiseGasBubble(water_grid):
    for i in range(cols):
        for j in range(rows):
            if water_grid[i, j, 0] >= T_ev: #Si la case contient de la vapeur
                if (j > 0 and water_grid[i, j-1, 0] < T_ev):
                    water_grid[i, j, 1] += 1 #On incrémente le compteur
                    if (water_grid[i, j, 1] >= beta):
                        tmp = water_grid[i, j-1, 0]
                        water_grid[i, j-1, 0] = water_grid[i, j, 0]
                        water_grid[i, j, 0] = tmp
                        water_grid[i, j-1, 1] = 0
                        water_grid[i, j, 1] = 0
                else:
                    water_grid[i, j, 1] = 0
C_comb = 10
grid = np.zeros((cols, rows))
water_grid = np.zeros((cols, rows, 2))
water_grid[:, :, 0] = CToK + 80  # Remplissage des températures

n_comb = int(grid.size*C_comb/100) #Nombre de cases contenant du combustible
for i in range(n_comb):
    #On place les cases de combustible aléatoirement
    x, y = random.randint(0, cols-1), random.randint(0, rows-1)
    while grid[x, y] != NON_FISSIBLE: #Tant que la case n'est pas vide on cherche une autre position
        x, y = random.randint(0, cols-1), random.randint(0, rows-1)
    grid[x, y] = UR_235 #On place du combustible à cet emplacement

neutrons = Neutrons() #Initialisation de la collection de neutrons

nb = 0
nbmax = 1000
time: NDArray = np.zeros(nbmax);
nbNeutron: NDArray = np.zeros(nbmax);
nbVapor: NDArray = np.zeros(nbmax);
tempMoyenne: NDArray = np.zeros(nbmax);
neutrons = Neutrons()
pos_neut_init = cellTocoord(cols//2, rows//2, 0) 
for _ in range(30):
    neutrons.addFastNeutron(pos_neut_init[0], pos_neut_init[1]) 

ntemp = 0
# Main loop
while running and nb < nbmax:
    screen.fill(noir)

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
    time[nb] = nb*delta_t
    nbNeutron[nb] = neutrons.nb_neutron
    tempMoyenne[nb] = np.mean(water_grid[:, :, 0])
    nbVapor[nb] = np.sum(water_grid[:, :, 0] >= T_ev)
    neutrons.deplacerWithConfinment()
    interactNeutronsWithWater(water_grid[:, :, 0], neutrons)
    handleHeatTransfer(water_grid)
    raiseGasBubble(water_grid)

    interactNeutronsWithUrXe(neutrons, grid)
    nb+=1
    
    paint(grid, water_grid, neutrons) 
    pygame.display.flip()

# Create plot
fig, ax1 = plt.subplots()
ax1.set_xlabel('Temps')
ax1.set_ylabel('Nombre de neutrons', color='r')
ax1.plot(time, nbNeutron, label='nombre de neutrons', color='r')
ax1.tick_params(axis='y', labelcolor='r')
# ax1.legend()

# ax2 = ax1.twinx()
# ax2.set_ylabel('Température moyenne')
# ax2.plot(time, tempMoyenne, linestyle='--', label='température moyenne')
# ax2.plot(time, np.ones_like(time)*T_ev, linestyle='--', label='température d\'ébullition')
# ax2.legend()

ax3 = ax1.twinx()
ax3.set_ylabel('Quantité de vapeur', color='b')
ax3.plot(time, nbVapor, linestyle='--', label='quantité de vapeur', color='b')
ax3.tick_params(axis='y', labelcolor='b')
# ax3.legend()

# Add labels and title
plt.title('Évolution du nombre de neutrons et de la vapeur en fonction du temps')
plt.legend()

# Show plot
plt.show()
pygame.quit()