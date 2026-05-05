from models import *
from numpy._typing import NDArray
import numpy as np
from simpleRandom import *
import pygame

class Neutrons:
    max_neutron: int = 10000
    nb_neutron: int = 0
    total_neutrons: int = 0

    # Le premier index de pos est la position en x 
    # et le second la position en y
    pos: NDArray

    # Le premier index de v est la vitesse en x, 
    # le second la vitesse en y 
    # et le troisième un booléen indiquant si le neutron est rapide ou lent
    v: NDArray

    # Un tableau d'angle pour chaque neutron
    angle: NDArray

    # Init des collections de neutrons
    def __init__(self):
        self.pos = np.zeros((self.max_neutron, 2))
        self.v = np.zeros((self.max_neutron, 3))
        self.angle = np.zeros(self.max_neutron)
        self.nb_neutron = 0;

    # Ajoute un neutron dans le tableau numpy
    def addNeutron(self, x, y):
        vitesse = getRandomSpeed()  # Répartition des neutrons rapides et lents
        self.addNeutronWithSpeed(x, y, vitesse)

    # Ajoute un neutron dans le tableau numpy
    def addNeutronWithSpeed(self, x, y, vitesse):
        # Pour garder une taille fixe en mémoire
        if (self.nb_neutron >= self.max_neutron):
            return;

        # On ajoute toujours à la position en cours (nbNeutron)
        self.pos[self.nb_neutron] = [x, y]
        self.angle[self.nb_neutron] = getRandomAngle()
        self.actu_vitesse(vitesse, self.nb_neutron)
        self.nb_neutron += 1
        self.total_neutrons += 1

    def addSlowNeutron(self, x, y):
        self.addNeutronWithSpeed(x, y, 1)

    def addFastNeutron(self, x, y):
        self.addNeutronWithSpeed(x, y, 3)

    def removeNeutron(self, index):
        if index < 0 or index >= self.nb_neutron:
            return
        self.pos[index] = self.pos[self.nb_neutron - 1]
        self.v[index] = self.v[self.nb_neutron - 1]
        self.angle[index] = self.angle[self.nb_neutron - 1]
        self.nb_neutron -= 1

    def deplacer(self):
        removed = 0;
        self.pos[:,:] += self.v[:, 0:2]
        for i in range(self.nb_neutron):
            if (
                self.pos[i, 0] < 0 or self.pos[i, 0] > width - rightMenuSize 
                or self.pos[i, 1] < 0 or self.pos[i, 1] > height
            ):  # Si le neutron sort de l'écran on le supprime
                self.removeNeutron(i)
                removed = removed + 1
        return removed

    def deplacerWithConfinment(self):
        removed = 0;
        self.pos[:,:] += self.v[:, :2]

        for i in range(self.nb_neutron):
            # Si neutron lent => est absorbé par le confinement
            if not self.v[i, 2] and (
                self.pos[i, 0] < 0 or self.pos[i, 0] > width - rightMenuSize 
                or self.pos[i, 1] < 0 or self.pos[i, 1] > height
            ):  # Si le neutron sort de l'écran on le supprime
                self.removeNeutron(i)
                removed = removed + 1
                continue

            # Si neutron rapide, est renvoyé et ralenti
            if (self.pos[i, 0] < 0):
                self.pos[i, 0] = 0
                # retourne horizontalement
                self.angle[i] = np.pi - self.angle[i]
                # on ralentis
                self.actu_vitesse(1, i)
            if (self.pos[i, 0] > width - rightMenuSize):
                self.pos[i, 0] = width - rightMenuSize
                # retourne horizontalement
                self.angle[i] = np.pi - self.angle[i]
                # on ralentis
                self.actu_vitesse(1, i)

            if (self.pos[i, 1] < 0):
                self.pos[i, 1] = 0
                # retourne horizontalement
                self.angle[i] = (2*np.pi) - self.angle[i]
                # on ralentis
                self.actu_vitesse(1, i)
            if (self.pos[i, 1] > height):
                self.pos[i, 1] = height
                # retourne horizontalement
                self.angle[i] = (2*np.pi) - self.angle[i]
                # on ralentis
                self.actu_vitesse(1, i)
        return removed

    def actu_vitesse(self, vitesse, index):
        vx = vitesse * np.cos(self.angle[index])
        vy = vitesse * np.sin(self.angle[index])
        self.v[index] = [vx, vy, vitesse == 3]

def handleHeatTransfer(T):
    # On calcule le transfert thermique dans chaque direction
    energy_right = -(T[1:, :] - T[:-1, :]) * c_s * 6040 * delta_t
    energy_bottom = -(T[:, 1:] - T[:, :-1]) * c_s * 6040 * delta_t
    # On applique le transfert d'énergie en positif et en négatif pour le départ et l'arrivée
    diff = np.zeros_like(T)
    diff[1:, :] += energy_right
    diff[:-1, :] -= energy_right
    diff[:, 1:] += energy_bottom
    diff[:, :-1] -= energy_bottom 
    T += diff / (m_eau * C_me)  # On met à jour

def interactNeutronsWithWater(T, neutrons: Neutrons):
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
                else:
                    # Idem pour l'absorption lente
                    absorption_lent = getRandomInteractLent()  
                    if absorption_lent == 1:
                        # Chaleur fournie par le neutron lent (concrètement négligeable)
                        T[grid_x, grid_y] += (
                            q_ad_slow * Ec_slow / (m_eau * C_me)
                        )  
                        # Le neutron lent est quant à lui absorbé donc il disparait
                        neutrons.removeNeutron(i)
                        water_abs_count += 1
    return water_abs_count

def interactNeutronsWithUrXe(neutrons, grid, T=None):
    fission_count = 0
    Xe_abs_count = 0

    for i in range(neutrons.nb_neutron):
        nx = neutrons.pos[i,0]
        ny = neutrons.pos[i,1]

        #Coordonnées du neutron cible dans la base des cases
        grid_x, grid_y = int(nx//cell_size), int(ny//cell_size) 

        #On verifie que le neutron soit bien dans l'écran
        if 0 > grid_x or grid_x >= cols or 0 > grid_y or grid_y >= rows: 
            continue

        #Si c'est un neutron lent et que la case contient du combustible fissile
        if grid[grid_x, grid_y] == UR_235 and not neutrons.v[i,2]: 
            fission_result = getRandomInteractLentFission() #On jete les dés pour la fission

            if fission_result == 0:
               continue

            #Si la fission s'effectue
            fission_count +=1 #On incrémente le compteur de fission

            if T is not None :
                T[grid_x, grid_y] += (fission_ctrl_factor*q_ad_fast*(frac_Elib_fiss*E_lib_fission)/(m_eau*C_me))

            conv_Xe_result = getRandomConvXe()

            if conv_Xe_result == 0 : #Si n'est pas converti en Xénon
                grid[grid_x, grid_y] = NON_FISSIBLE

            else : #Si est converti en Xénon
                grid[grid_x, grid_y] = XE_135 

            # On ajoute un conbustible autrepart
            res = np.argwhere(grid == NON_FISSIBLE) #On trouve les (i, j) pour les cases de réserve
            if (len(res) > 0):
                rx, ry = res[random.randint(0, len(res)-1)] #On extrait aléatoirement les coordonnées d'une réserve dispo
                grid[rx, ry] = UR_235 #On réinsère du combustible à cet emplacement

            #On émet 3 neutrons rapides avec des directions aléatoires
            for _ in range(3) : 
                neutrons.addFastNeutron(neutrons.pos[i,0], neutrons.pos[i,1])

            # On retire le neutron absorbé
            neutrons.removeNeutron(i)

        #Si la case contient du Xénon et qu'on a un neutron lent
        elif grid[grid_x, grid_y] == XE_135 and not neutrons.v[i,2]: 
            Xe_abs_result = getRandomInteractLentXe() #On lance les dés pour l'absorption

            if Xe_abs_result == 0:
               continue
            
            #Si il y a absorption par le Xénon
            Xe_abs_count +=1 #On incrémente le compteur associé
            grid[grid_x, grid_y] = NON_FISSIBLE #La case devient une réserve
            neutrons.removeNeutron(i)

    return (fission_count, Xe_abs_count)

def interactNeutronsWithControlRod(neutrons: Neutrons, rod_rect: pygame.Rect):
    removed = 0
    for i in range(neutrons.nb_neutron):
        if not neutrons.v[i, 2]:
            nx = neutrons.pos[i, 0]
            ny = neutrons.pos[i, 1]
        
            # Si le centre du neutron est dans le rectangle de la barre
            if rod_rect.collidepoint(nx, ny):
                neutrons.removeNeutron(i)
                removed += 1
            
    return removed