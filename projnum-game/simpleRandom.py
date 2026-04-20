import random
import numpy as np
from models import *
from numpy._typing import NDArray

class random_var:
    valList: NDArray
    size: int
    index: int = 0
    def __init__(self, size, generateRandom):
        self.valList = np.zeros(size)
        self.size = size
        for i in range(size):
            self.valList[i] = generateRandom()

def getNextVal(rdv: random_var):
    rdv.index = (rdv.index + 1) % rdv.size
    return rdv.valList[rdv.index]

angle_var = random_var(1000, lambda: random.uniform(0, 2 * np.pi))
getRandomAngle = lambda: getNextVal(angle_var)

speed_var = random_var(1000, lambda: random.choices([1, 3], weights=[100 - p_n0_rapides, p_n0_rapides])[0])
getRandomSpeed = lambda: getNextVal(speed_var)

interact_rapide_var = random_var(10000, lambda: random.choices([0, 1], weights=[100 - p_int_rapide, p_int_rapide])[0])
getRandomInteractRapide = lambda: getNextVal(interact_rapide_var)

interact_lent_var = random_var(10000, lambda: random.choices([0, 1], weights=[100 - p_abs_lente, p_abs_lente])[0])
getRandomInteractLent = lambda: getNextVal(interact_lent_var)
