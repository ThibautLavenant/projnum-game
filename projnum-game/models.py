from abc import ABC, abstractmethod

# Defining the interface
class ModeStateModel(ABC):
    @abstractmethod
    def prepare(self, screen):
        """Prepare le mode"""
        pass

    @abstractmethod
    def update(self, events, setMode):
        """Update le mode pour jouer la simulation"""
        pass

    @abstractmethod
    def paint(self, screen):
        """Dessine l'état actuel de la simulation"""
        pass

    @abstractmethod
    def export_datas(self):
        """Exporte les données de la simulation"""
        pass

# Pygame variables for window handling
width, height = 800, 600
rightMenuSize = 200
fps = 60

noir = (10, 10, 10)
blanc = (245, 245, 245)
violet = (148, 0, 211)

bleu = (50, 100, 255)
jaune = (255, 255, 0)
orange = (255, 165, 0)
rouge = (255, 50, 50)

vertUr = (52, 201, 36) #Vert pomme pour l'Uranium
grisVi = (158, 158, 158) #Gris souris pour le vide
violetXe = (121, 28, 248) #Indigo pour le Xénon

cell_size = 20 #Taille des cellules
cols, rows = (width - rightMenuSize)//cell_size, height//cell_size
border = 5 #Bordure inter-cellules
delta_t = 0.01 #Écart temporel d'une itération à l'autre (en s)

# Variables physiques de la modélisation
pxTom = 10e-2/20 #Facteur de conversion en m/px (permet de passer de px à m, ici 1px = 0.05cm =5e-4m)
CToK = 273.15 #Conversion Celsius-Kelvin
JTokWh = 2.77778e-7 #Pour convertir des Joules en kWh
JToMeV = 6.242e12 #Pour convertir des Joules en MeV
Gamma = 50 #Facteur d'échelle pour les échanges thermiques, ici on prend 1s de simu = 50s réelles

c_s = cell_size*pxTom #Taille réelle des cellules
v_b = 0.06 #Vitesse réelle des bulles en m/s
beta = int(c_s/(v_b*10*delta_t)) #Tick pour la remontée des bulles, *10 pour la simu

# Propriétés eau
T0 = CToK + 20 #Température initiale de l'eau = température ambiante donc 25°C
T_ev = CToK + 100 #Température d'évaporation de l'eau (à p ambiante)
rho_eau = 997 #Masse volumique de l'eau en kg/m^3
C_me = 4180 #Capacité thermique massique de l'eau en J/kg
m_eau = rho_eau*(cell_size*pxTom)**3 #Masse d'eau dans une cellule

# Propriétés neutrons
m_n = 1.6749275e-27 #Masse d'un neutron en kg
Ec_fast = 3e-13 #Énergie cinétique en J des neutrons rapides de l'ordre de 2MeV
Ec_slow = 4e-21 #Énergie cinétique en J des neutrons lents de l'ordre de 0.025eV
v_real_fast = (2*Ec_fast/m_n)**0.5
v_real_slow = (2*Ec_slow/m_n)**0.5
v_sim_fast = 3
v_sim_slow = 1
nbr_nav = 5 #Nombre de neutrons intéragissant avant évaporation --> pour déterminer le facteur d'adaptation voir ligne suivante
q_ad_slow = m_eau*C_me*(T_ev-T0)/(Ec_slow*nbr_nav) #Facteur d'adaptation pour la simu --> permet de chauffer plus vite par les neutrons thermiques
q_ad_fast = m_eau*C_me*(T_ev-T0)/(Ec_fast*nbr_nav) #Facteur d'adaptation pour la simu --> permet de chauffer plus vite par les neutrons thermiques

# Probas
p_int_rapide = 10 #Probabilité d'intéraction des neutrons rapides avec l'eau en %
p_abs_lente = 0.1*p_int_rapide #Probabilité d'absorption des neutrons lents en %
p_n0_rapides = 50 #Proportion de neutrons rapides à l'apparition en %
p_fission = 100 #Probabilité de fission par les neutrons lents en %
p_Xe_abs = 100 #Probabilité d'absorption des neutrons lents par le Xénon en %
p_conv_Xe = 10 #Probabilité de conversion du combustible fissioné en Xénon en %

# Paliers de température
Interval = (T_ev-T0)/4 #Étendue divisé par le nbr d'intervales souhaités
Palier1 = T0+Interval #Premier palier de température ici de 20°C à 40°C
Palier2 = T0+2*Interval #Second palier donc de 40°C à 60°C
Palier3 = T0+3*Interval #Second palier donc de 40°C à 60°C

# Thermo
k1 = 2.4e-3*Gamma #Constante pour la loi de Newton - conducto convectif à l'interface supérieure
k2 = 2.4e-5*Gamma #Constante pour la loi de Fourier - conduction au sein du bassin

# Pompage
alpha_p = 50 #Pourcentage de puissance de la pompe
dT_max_p = 0.1 #Nbr de Kelvin retirés chaque seconde dans le cas où alpha = 100
T_min_p = 50+CToK #Température minimale de refroidissement par pompage
eta_p = 0.33 #Rendement typique d'un réacteur à eau pressurisée
dT_p = alpha_p/100*dT_max_p*delta_t*Gamma #Valeur de \Delta T adapté à la simu

# Fission
neut_gen_fission = 3 #Nombre de neutrons générés par une fission
E_lib_fission = 1.95e-11 #Énergie libérée lors de la fission de l'uranium 235
n_k = 100 #Nombre de neutrons évalués pour déterminer k

def cellTocoord(c, r, param): #c --> colonne (x) et r --> ligne (y)
    if param == 0 :
        return c*cell_size+cell_size//2, r*cell_size+cell_size//2 #Conversion de cellule vers coordonnées
    else:
        return (int(c//cell_size), int(r//cell_size)) #Conversion des coordonnées vers cellule
