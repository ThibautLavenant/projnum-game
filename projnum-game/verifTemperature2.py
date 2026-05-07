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
pygame.display.set_caption("Vérification temperature")
clock = pygame.time.Clock()
running = True

activeModeState: ModeStateModel = None
cols = 2;
rows = 1;

grid: NDArray
grid = np.zeros((cols, rows))
grid[0, 0] = T0  # Remplissage des températures
grid[1, 0] = T_ev;
nb = 0
nbmax = 1500
time: NDArray = np.zeros(nbmax);
temp: NDArray = np.zeros((2,nbmax));

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
    time[nb] = nb*delta_t
    temp[0, nb] = grid[0,0]
    temp[1, nb] = grid[1,0]
    nb+=1
    print(f"C0={grid[0,0]}, C1={grid[1,0]}, nb={nb}")
    paint(screen)  
    pygame.display.flip()
    # clock.tick(fps)

# Create plot
plt.plot(time, temp[0, :], color='blue', label='C0')
plt.plot(time, temp[1, :], color='red', label='C1')

# Add labels and title
plt.xlabel('Time')
plt.ylabel('Temperature')
plt.title('Temperature Evolution')
plt.legend()

# Show plot
plt.show()
pygame.quit()