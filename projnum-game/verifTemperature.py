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
pygame.display.set_caption("Vérification temperature décroissance exp")
clock = pygame.time.Clock()
running = True

activeModeState: ModeStateModel = None
cols = 2;
rows = 1;

grid: NDArray
grid = np.zeros((cols, rows))
grid[0, 0] = T_ev  # Remplissage des températures
grid[1, 0] = T0;
nb = 0
nbmax = 1500
time: NDArray = np.zeros(nbmax);
temp: NDArray = np.zeros(nbmax);

def paint(screen):
    # Affichage des cases d'eau
    for i in range(cols):
        for j in range(rows):
            if grid[i, j] >= T_ev:  # Si la case contient de la vapeur
                color = noir
            else:
                if grid[i, j] < Palier1:
                    color = bleu
                elif grid[i, j] < Palier2:
                    color = jaune
                elif grid[i, j] < Palier3:
                    color = orange
                elif grid[i, j] < T_ev:
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


# Main loop
while running and nb < nbmax:
    screen.fill(noir)

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
    handleHeatTransfer(grid[:, :])
    grid[1, 0] = T0; # Isotherme
    time[nb] = nb*delta_t
    temp[nb] = grid[0,0]
    nb+=1
    paint(screen)
    pygame.display.flip()
    # clock.tick(fps)


# Compute theroretical temperature decay
tau = (m_eau * C_me)/(lambda_eau * c_s) #Constante de temps de décroissance 
theoricalTemp = T0 + (T_ev - T0)*np.exp(-time[::100]/tau)

# Create plot
plt.plot(time[::100], temp[::100], color='blue', marker="+", label='Modèle')
plt.plot(time[::100], theoricalTemp, color='red', label='Théorie')

# Add labels and title
plt.xlabel('Temps (s)')
plt.ylabel('Température (K)')
plt.title('Évolution de la température')
plt.legend()

# Show plot
plt.show()
pygame.quit()