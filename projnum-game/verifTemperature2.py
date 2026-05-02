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
cols = 60;
rows = 1;

grid: NDArray
grid = np.zeros((cols, rows))
grid[:cols//2, 0] = T0  # Remplissage des températures
grid[cols//2:, 0] = T_ev;
nb = 0
nbmax = 250*6
time: NDArray = np.zeros(nbmax);
temp: NDArray = np.zeros((7,cols));

ntemp = 0
# Main loop
while running and nb < nbmax:
    screen.fill(noir)

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
    else :
        if (nb%(nbmax//6) == 0):
            temp[ntemp, :] = grid[:,0]
            ntemp += 1
        for _ in range(300):
            handleHeatTransfer(grid[:, :])
        nb+=1
    
temp[6, :] = grid[:,0]

# Create plot
plt.plot(range(cols), temp[0, :], label='t0')
plt.plot(range(cols), temp[1, :], label='t1')
plt.plot(range(cols), temp[2, :], label='t2')
plt.plot(range(cols), temp[3, :], label='t3')
plt.plot(range(cols), temp[4, :], label='t4')
plt.plot(range(cols), temp[5, :], label='t5')
plt.plot(range(cols), temp[6, :], label='t6')

# Add labels and title
plt.xlabel('Position horizontale')
plt.ylabel('Température')
plt.title('Évolution de la température en fonction du temps')
plt.legend()

# Show plot
plt.show()
pygame.quit()