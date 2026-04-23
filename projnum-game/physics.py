from models import *
import numpy as np

def handleHeatTransfer(T):
    # On calcule le transfert thermique dans chaque dirrection
    energy_right = -(T[1:, :] - T[:-1, :]) * c_s * 60400 * delta_t
    energy_bottom = -(T[:, 1:] - T[:, :-1]) * c_s * 60400 * delta_t
    # On applique le transfert d'énergie en positif et en négatif pour le départ et l'arrivée
    diff = np.zeros_like(T)
    diff[1:, :] += energy_right
    diff[:-1, :] -= energy_right
    diff[:, 1:] += energy_bottom
    diff[:, :-1] -= energy_bottom 
    T += diff / (m_eau * C_me)  # On met à jour