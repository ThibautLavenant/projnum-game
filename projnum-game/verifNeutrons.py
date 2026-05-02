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

def paint(grid, neutrons):
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

for C_comb in [3, 2, 1]:
    grid = np.zeros((cols, rows))
    water_grid = np.zeros((cols, rows, 2))
    water_grid[:, :, 0] = T0  # Remplissage des températures

    n_comb = int(grid.size*C_comb/100) #Nombre de cases contenant du combustible
    for i in range(n_comb):
        #On place les cases de combustible aléatoirement
        x, y = random.randint(0, cols-1), random.randint(0, rows-1)
        while grid[x, y] != NON_FISSIBLE: #Tant que la case n'est pas vide on cherche une autre position
            x, y = random.randint(0, cols-1), random.randint(0, rows-1)
        grid[x, y] = UR_235 #On place du combustible à cet emplacement

    neutrons = Neutrons() #Initialisation de la collection de neutrons

    nb = 0
    nbmax = 2000
    time: NDArray = np.zeros(nbmax);
    nbNeutron: NDArray = np.zeros(nbmax);
    neutrons = Neutrons()
    pos_neut_init = cellTocoord(cols//2, rows//2, 0) 
    for _ in range(50):
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
        neutrons.deplacerWithConfinment()
        interactNeutronsWithUrXe(neutrons, grid)
        nb+=1
        
        paint(grid, neutrons) 
        pygame.display.flip()

    # Create plot
    plt.plot(time, nbNeutron, label=f'C{C_comb}')

# Add labels and title
plt.xlabel('Temps')
plt.ylabel('Nombre de neutrons')
plt.title('Évolution du nombre de neutrons à différentes concentrations')
plt.legend()

# Show plot
plt.show()
pygame.quit()