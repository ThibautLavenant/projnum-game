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

def paint(water_grid, neutrons):
    # Affichage des cases d'eau
    for i in range(cols):
        for j in range(1):
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

    # affichage des neutrons
    for i in range(neutrons.nb_neutron):
        color = violet if neutrons.v[i, 2] else blanc
        pygame.draw.rect(screen, 
                         color, 
                         (int(neutrons.pos[i, 0]), 
                          int(neutrons.pos[i, 1]), 
                          3, 
                          3))

def interactNeutronsWithWater(T, neutrons: Neutrons, posAbsorbed: NDArray, posSlowed: NDArray):
    water_abs_count = 0
    for i in range(neutrons.nb_neutron):
        # Coordonnées du neutron cible dans la base des cases
        grid_x = int(neutrons.pos[i, 0] // cell_size)
        grid_y = int(neutrons.pos[i, 1] // cell_size)

        if (
            0 <= grid_x < cols and 0 <= grid_y < rows
        ):  # On verifie que le neutron soit bien dans l'écran
            if (
                T[grid_x, grid_y] <= T_ev
            ):  # Si la case contient de l'eau liquide

                if neutrons.v[i, 2]:
                    # On lance les dés pour l'intéraction rapide
                    interact_rapide = getRandomInteractRapide()  
                    if interact_rapide == 1:
                        # Chaleur fournie par le neutron rapide
                        T[grid_x, grid_y] += (
                            q_ad_fast * (Ec_fast - Ec_slow) / (m_eau * C_me)
                        )  
                        # Ralentissement du neutron rapide
                        neutrons.actu_vitesse(1, i)
                        posSlowed[grid_x] += 1 #On compte le nombre de neutrons absorbés dans cette colonne pour faire le graphique
                else:
                    # Idem pour l'absorption lente
                    absorption_lent = getRandomInteractLent()  
                    if absorption_lent == 1:
                        # Chaleur fournie par le neutron lent (concrètement négligeable)
                        T[grid_x, grid_y] += (
                            q_ad_slow * Ec_slow / (m_eau * C_me)
                        )
                        # Le neutron lent est quant à lui absorbé donc il disparait
                        posAbsorbed[grid_x] += 1 #On compte le nombre de neutrons absorbés dans cette colonne pour faire le graphique
                        neutrons.removeNeutron(i)
                        water_abs_count += 1

posAbsorbed: NDArray = np.zeros(cols);
posSlowed: NDArray = np.zeros(cols);
for i in range(1000):
    print(i)
    water_grid = np.zeros((cols, 1, 2))
    water_grid[:, :, 0] = T0  # Remplissage des températures
    neutrons = Neutrons() #Initialisation de la collection de neutrons

    nb = 0
    nbmax = 2000
    time: NDArray = np.zeros(nbmax);
    neutrons = Neutrons()
    for _ in range(20):
        neutrons.addNeutronWithSpeedAndAngle(0, cell_size // 2, 3, 0) 

    ntemp = 0
    # Main loop
    while running and nb < nbmax and neutrons.nb_neutron > 0:
        screen.fill(noir)
        water_grid[:, :, 0] = T0  # Remplissage des températures
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        time[nb] = nb*delta_t
        neutrons.deplacer()
        interactNeutronsWithWater(water_grid[:, :, 0], neutrons, posAbsorbed, posSlowed)
        nb+=1

        paint(water_grid, neutrons) 
        # clock.tick(fps)
        pygame.display.flip()


# Create plot
plt.plot(range(cols), posAbsorbed, label=f'Neutrons lents absorbés', color='r')
plt.plot(range(cols), posSlowed, label=f'Neutrons rapides ralentis', color='b')
meanCapture = np.mean(posAbsorbed * range(cols)) * cols / np.sum(posAbsorbed)
meanSlowed = np.mean(posSlowed * range(cols)) * cols / np.sum(posSlowed)
plt.vlines([meanCapture], 0, np.max(posSlowed), label=f'Position moyenne d\'absorbtion'   , color='r', linestyle='dotted')
plt.vlines([meanSlowed], 0, np.max(posSlowed), label=f'Position moyenne de ralentissement', color='b', linestyle='dotted')

# Add labels and title
plt.xlabel('Position en X')
plt.ylabel('Nombre de neutrons absorbés ou ralentis')
plt.title('Évolution du nombre de neutrons absorbés selon la distance d\'émission')
plt.legend()

# Show plot
plt.show()
pygame.quit()