import random  # Pour les tirages aléatoires
import sys  # Pour quitter proprement
import pygame  # Le module Pygame
from pygame.locals import *
import pygame.freetype  # Pour afficher du texte
import math
import time
import json
import os

# Fonction pour sauvegarder les données dans un fichier JSON
def save_data(data, filename='save_data.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Fonction pour charger les données depuis un fichier JSON
def load_data(filename='save_data.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return {}

data = load_data()

# === Initialisation de Pygame et des modules ===
pygame.init()  # Initialisation de Pygame
pygame.freetype.init()  # Initialisation des polices
pygame.mixer.init(frequency=44100, size=-16, channels=2)  # Initialisation du son

# === Constantes ===
BLANC = (255, 255, 255)
NOIR = (0, 0, 0)
RAYON_BALLE = 10

# Taille de la fenêtre et ajustements dynamiques
info = pygame.display.Info()
width, height = info.current_w, info.current_h
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Cr4zy G4me M4nia F0r Hardc0re G@MerZ")

delta_w = width / 1080
delta_h = height / 720
RAYON_BALLE = 10 * delta_w
XMIN, YMIN = 0, 0
XMAX, YMAX = width, height

# Pour limiter le nombre d'images par seconde
clock = pygame.time.Clock()

# === Gestion des Polices ===
font_path = 'nintendo-nes-font.otf' # Chargement police Nintendo NES
font_size1 = int(13 * delta_w)
font_size2 = int(17 * delta_w)
font_size3 = int(27 * delta_w)
font_size4 = int(40 * delta_w)
font_size5 = int(100 * delta_w)

# Chargement des polices avec différentes tailles
small_font = pygame.font.Font(font_path, font_size1)
mid_font = pygame.font.Font(font_path, font_size2)
big_font = pygame.font.Font(font_path, font_size3)
huge1_font = pygame.font.Font(font_path, font_size4)
huge2_font = pygame.font.Font(font_path, font_size5)


# Intro (lancement)
screen.fill(NOIR)
intro_img = pygame.image.load("images/logo_game.png")
intro_img = pygame.transform.scale(intro_img, (width/1.5, height/1.5))
konami_img = pygame.image.load("images/konami_logo.jpg")
konami_img = pygame.transform.scale(konami_img, (width/2, height/3))
screen.blit(intro_img, (width/6, height/6 - 100*delta_h))
screen.blit(konami_img, (width/10, height/6 + 250*delta_h))
intro_text = huge1_font.render("- 1991", True, (200,200,200))
intro_rect = intro_text.get_rect(x = width/10 + 530*delta_w, y = height/6 + 350*delta_h)
screen.blit(intro_text, intro_rect)
pygame.display.flip()
intro_sound = pygame.mixer.Sound("sounds/intro.mp3")
intro_sound.play()
time.sleep(2)

# === Chargement des Sons ===
pygame.mixer.music.load("sounds/music_menu.mp3")
click_sound = pygame.mixer.Sound("sounds/click.wav")
coin_sound = pygame.mixer.Sound("sounds/pickupCoin.wav")
coin_sound.set_volume(0.5)
raquette_sound = pygame.mixer.Sound("sounds/hit.wav")
raquette_sound.set_volume(0.8)
dialogue_sound = pygame.mixer.Sound("sounds/dialogue.wav")
dialogue_sound.set_volume(0.7)
game_over_sound = pygame.mixer.Sound("sounds/game_over_sound.mp3")
boom_sound = pygame.mixer.Sound("sounds/explosion.wav")
beat_boss_sound = pygame.mixer.Sound("sounds/beat_boss.wav")

# Volume de la musique
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)  # Décommenter pour jouer la musique en boucle

# === Interface Utilisateur (Boutons) ===
button_menu_x, button_menu_y = 250 * delta_w, 80 * delta_h
button_surface = pygame.Surface((button_menu_x, button_menu_y))

# Rendre le texte sur le bouton
text = mid_font.render("Lancer le jeu", True, NOIR)
text_rect = text.get_rect(center=(button_surface.get_width() / 2, button_surface.get_height() / 2))

# Créer un objet pygame.Rect pour définir les limites du bouton
button_rect = pygame.Rect((width - button_menu_x) // 2, 125, button_menu_x, button_menu_y)

# === Gestion des Arrière-plans ===
backgrounds = []
width_bg = 1400 * screen.get_width() / 1080

# Chargement des images d'arrière-plan
for i in range(1, 4):
    background = pygame.image.load(f'images/{i}background{i}.png')
    background = pygame.transform.scale(background, (width_bg, width_bg))
    background_rect = background.get_rect(center=((width - width_bg) // 2, (height - width_bg) // 2))
    backgrounds.append((background, background_rect))  # Ajouter en tuple (surface, rect)

# Vitesse de défilement du parallaxe
speed_parallax = 0.1

class Money:
    def __init__(self):
        self.money = 10
        self.shop = False
        self.texte_blanc = big_font.render(f"SALAIRE: {self.money} DOLLARS", True, BLANC)
        self.texte_noir = big_font.render(f"SALAIRE: {self.money} DOLLARS", True, NOIR)
        self.degats_owned = 0
        self.plus_profit = 1
        self.plus_dmg = 0
        self.depense = 0
        self.boom = 256
        self.dgt_boom = True
        self.drone = 512
        self.dgt_drone = True

    def to_dict(self):
        """Convertit les données de la classe en dictionnaire pour sauvegarde."""
        return {
            'money': self.money,
            'shop': self.shop,
            'degats_owned': self.degats_owned,
            'plus_profit': self.plus_profit,
            'plus_dmg': self.plus_dmg,
            'depense': self.depense,
            'boom': self.boom,
            'dgt_boom': self.dgt_boom,
            'drone': self.drone,
            'dgt_drone': self.dgt_drone
        }

    def from_dict(self, data):
        """Met à jour les données de la classe à partir d'un dictionnaire."""
        self.money = data.get('money', 10)
        self.shop = data.get('shop', False)
        self.degats_owned = data.get('degats_owned', 0)
        self.plus_profit = data.get('plus_profit', 1)
        self.plus_dmg = data.get('plus_dmg', 0)
        self.depense = data.get('depense', 0)
        self.boom = data.get('boom', 256)
        self.dgt_boom = data.get('dgt_boom', True)
        self.drone = data.get('drone', 512)
        self.dgt_drone = data.get('dgt_drone', True)
        # Recréer les rendus de texte à partir de la nouvelle valeur de money
        self.update_text()

    def update_text(self):
        """Met à jour les textes à afficher avec la valeur actuelle de money."""
        self.texte_blanc = big_font.render(f"SALAIRE: {self.money} DOLLARS", True, BLANC)
        self.texte_noir = big_font.render(f"SALAIRE: {self.money} DOLLARS", True, NOIR)
        
    def ajouter(self, n):
        self.money += n
        self.texte_blanc = big_font.render(f"SALAIRE: {self.money} DOLLARS", True, BLANC)
        self.texte_noir = big_font.render(f"SALAIRE: {self.money} DOLLARS", True, NOIR)
    
    def enlever(self, n):
        if self.money - n >= 0:
            self.money -= n
        self.texte_blanc = big_font.render(f"SALAIRE: {self.money} DOLLARS", True, BLANC)
        self.texte_noir = big_font.render(f"SALAIRE: {self.money} DOLLARS", True, NOIR)

money = Money()

class Balle:
    def __init__(self):
        self.x, self.y = (400, 400)
        self.vitesse = 8*delta_w  # vitesse initiale
        self.sur_raquette = True
        self.rebondx = False
        self.rebondy = False
        self.vitesse_par_angle(60, 0 + 1)  # vecteur vitesse
    
    def vitesse_par_angle(self, angle, n):
        self.vx = self.vitesse*n * math.cos(math.radians(angle))
        self.vy = -self.vitesse*n * math.sin(math.radians(angle))
    
    def afficher(self):
        pygame.draw.rect(screen, BLANC,
                         (int(self.x-RAYON_BALLE), int(self.y-RAYON_BALLE),
                          2*RAYON_BALLE, 2*RAYON_BALLE), 0)

    def rebond_raquette(self, raquette):   
        diff = raquette.x - self.x
        longueur_totale = raquette.longueur/2 + RAYON_BALLE
        angle = 90 + 80 * diff/longueur_totale
        self.vitesse_par_angle(angle, 0 + 1)
        money.enlever(menu.level_selected)
        raquette_sound.play()

    def deplacer(self, raquette):
        if self.sur_raquette:                      
            self.y = raquette.y - 2*RAYON_BALLE    
            self.x = raquette.x                  
        else:                                      
            if self.rebondx:
                self.vy = -self.vy
                self.rebondx = False
            if self.rebondy:
                self.vx = -self.vx
                self.rebondy = False
            self.x += self.vx                      # décaler toutes les lignes
            self.y += self.vy                      # suivantes
            if raquette.collision_balle(self) and self.vy > 0:
                self.rebond_raquette(raquette)
            if self.x + RAYON_BALLE > XMAX:
                self.vx = -self.vx
            if self.x - RAYON_BALLE < XMIN:
                self.vx = -self.vx
            if self.y + RAYON_BALLE > YMAX:
                print("perdu")
                game_over_sound.play()
                jeu.perdu = True
                menu.select_level_clicked = False
                self.sur_raquette = True
            if self.y - RAYON_BALLE < YMIN:
                self.vy = -self.vy

            
class Raquette: # classe à rajouter entre Balle et Jeu
    def __init__(self):
        self.x = (XMIN+XMAX)/2
        self.y = YMAX - RAYON_BALLE
        self.longueur = 15*RAYON_BALLE


    def afficher(self):
        pygame.draw.rect(screen, BLANC,
                         (int(self.x-self.longueur/2), int(self.y-RAYON_BALLE),
                          self.longueur, 2*RAYON_BALLE), 0)

    def deplacer(self, x):
        if x - self.longueur/2 < XMIN:
            self.x = XMIN + self.longueur/2
        elif x + self.longueur/2 > XMAX:
            self.x = XMAX - self.longueur/2
        else:
            self.x = x
            
    def collision_balle(self, balle):
        vertical = abs(self.y - balle.y) < 2*RAYON_BALLE
        horizontal = abs(self.x - balle.x) < self.longueur/2 + RAYON_BALLE
        return vertical and horizontal

class Projectile:
    def __init__(self, x, y, vitesse, color):
        self.x = x
        self.y = y
        self.vitesse = vitesse
        self.largeur = 5*delta_w  # Largeur du projectile
        self.hauteur = 10*delta_h  # Hauteur du projectile
        self.color = color

    def deplacer(self):
        """Déplacer le projectile vers le bas."""
        self.y += self.vitesse

    def afficher(self):
        """Afficher le projectile à l'écran."""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.largeur, self.hauteur))
    
    def collision(self, raquette):
        """Vérifier la collision avec la raquette."""
        return raquette.x - (15*RAYON_BALLE) / 2 <= self.x <= raquette.x + (15*RAYON_BALLE) / 2 and \
               raquette.y <= self.y <= YMAX

class Brique:   
    def __init__(self, x, y, vie):
        self.x = x
        self.y = y
        self.y_original = y  # On garde la position de départ pour l'oscillation
        self.vie = vie
        self.longueur = width // 18
        self.largeur = height // 18
        self.color = (255, 255, 255)
        self.oscillation_offset = 0  # Valeur initiale de l'oscillation
        self.oscillation_vitesse = 0.01  # Vitesse de l'oscillation
        self.oscillation_amplitude = 100 * delta_h  # Amplitude de l'oscillation
        self.osciller_active = False  # Par défaut, les briques ne bougent pas

        self.tir_intervalle = 5000  # Intervalle de tir en millisecondes
        self.dernier_tir = pygame.time.get_ticks()  # Temps du dernier tir
        self.projectiles = []  # Liste des projectiles tirés par la brique
        
        self.regen_intervalle = 5000
        self.dernier_regen = pygame.time.get_ticks()
        self.start_regen = 10

    def en_vie(self):
        return self.vie > 0

    def activer_oscillation(self):
        """Méthode pour activer l'oscillation de la brique."""
        self.osciller_active = True

    def desactiver_oscillation(self):
        """Méthode pour désactiver l'oscillation de la brique."""
        self.osciller_active = False

    def osciller(self):
        """Gère le mouvement d'oscillation si activé."""
        if self.osciller_active:
            # Calcul du décalage d'oscillation avec une fonction sinusoïdale
            self.oscillation_offset = math.sin(pygame.time.get_ticks() * self.oscillation_vitesse) * self.oscillation_amplitude
            self.y = self.y_original + self.oscillation_offset  # Appliquer le décalage à la position y

    def avant_tirer_projectile(self):
        maintenant = pygame.time.get_ticks()
        if maintenant - self.dernier_tir > self.tir_intervalle:
            self.dernier_tir = maintenant
            # Créer un projectile et l'ajouter à la liste des projectiles
            projectile = Projectile(self.x, self.y + self.largeur / 2, 5, (255, 0, 0))  # Projectile rouge descendant
            self.projectiles.append(projectile)

    def tirer_projectile(self, index):  # Ajout de l'index de la brique
        """Méthode pour tirer un projectile à partir de la brique si c'est une brique paire."""
        if menu.level_selected == 11:
            # Tirer seulement si brique dans la liste
            if index % 20 == 0 and self.en_vie():
                self.avant_tirer_projectile()
        if menu.level_selected == 13:
            if index % 8 == 0 and index < 16 and self.en_vie():
                self.avant_tirer_projectile()
        if menu.level_selected == 14:
            if (index == 0 or index == 15) and self.en_vie():
                self.avant_tirer_projectile()
        if menu.level_selected == 17:
            if (index == 7 or index == 8) and self.en_vie():
                self.avant_tirer_projectile()
        if menu.level_selected == 20:
            if self.en_vie() and self in jeu.regen:
                self.avant_tirer_projectile()

    def mettre_a_jour_projectiles(self):
        """Met à jour la position des projectiles et les supprime s'ils sortent de l'écran."""
        for projectile in self.projectiles:
            projectile.deplacer()
            if projectile.y > height:  # Si le projectile sort de l'écran
                self.projectiles.remove(projectile)
    
    def regeneration(self):
        maintenant = pygame.time.get_ticks()
        if self.vie == self.start_regen - 1:
            self.dernier_regen = maintenant
        if maintenant - self.dernier_regen > self.regen_intervalle and self.vie < self.start_regen:
            self.dernier_regen = maintenant
            self.vie += 1

    def afficher(self):
        if menu.level_selected in jeu.liste_acces:
            if jeu.perdu:
                jeu.briques = [Brique(width + 10000*delta_w, height + 10000*delta_h, 1)]  # Éloigne toutes les briques si on a perdu

            if menu.level_selected == 1:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    jeu.briques = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 250*delta_h, 1) for i in range(16)]  # Niveau 1 : ligne simple
                
            elif menu.level_selected == 2:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    jeu.briques = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), (150 + (abs(i - 8) * 25))*delta_h, 2) for i in range(16)]  # Niveau 2 : effet miroir symétrique

            elif menu.level_selected == 3:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Triangle pointant vers le bas
                    jeu.briques = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), (150 + j * 50)*delta_h, 2) for j in range(5) for i in range(5 - j)] + \
                                  [Brique(width - 38*delta_w - i * (self.longueur + 7*delta_w), (150+ j * 50)*delta_h , 3) for j in range(5) for i in range(5 - j)]

            elif menu.level_selected == 4:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Smile : yeux et bouche
                    jeu.briques = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 150*delta_h, 4) for i in [5, 10]] + \
                                  [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 200*delta_h, 4) for i in range(4, 12)] + \
                                  [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 250*delta_h, 3) for i in [6, 7, 8, 9]]  # Niveau 4 : smiley

                    jeu.obstacle = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 350*delta_h, 20000) for i in range(5, 11)]

            elif menu.level_selected == 5:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Forme de cœur améliorée avec ajout de briques "DRONE"
                    jeu.briques = [
                        Brique(38*delta_w + i * (self.longueur + 7*delta_w), 150*delta_h, 5) for i in [6, 9]
                    ] + [
                        Brique(38*delta_w + i * (self.longueur + 7*delta_w), 200*delta_h, 4) for i in [5, 7, 8, 10]
                    ] + [
                        Brique(38*delta_w + i * (self.longueur + 7*delta_w), 250*delta_h, 5) for i in [5, 10]
                    ] + [
                        Brique(38*delta_w + i * (self.longueur + 7*delta_w), 300*delta_h, 4) for i in [5, 10]
                    ] + [
                        Brique(38*delta_w + i * (self.longueur + 7*delta_w), 350*delta_h, 5) for i in [6, 9]
                    ] + [
                        Brique(38*delta_w + i * (self.longueur + 7*delta_w), 400*delta_h, 4) for i in [7, 8]
                    ]
                    
                    jeu.boom =[
                        Brique(38*delta_w + i * (self.longueur + 7*delta_w), 400*delta_h, 2005) for i in [1, 14]
                    ]
                    
        
            elif menu.level_selected == 6:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Carré vide (contour)
                    jeu.briques = [Brique(38*delta_w + (i + 6) * (self.longueur + 7*delta_w), 150*delta_h, 6) for i in range(3)] + \
                                  [Brique(38*delta_w + (i + 6) * (self.longueur + 7*delta_w), 250*delta_h, 5) for i in range(3)] + \
                                  [Brique(38*delta_w + 6 * (self.longueur + 7*delta_w), 200*delta_h, 5), Brique(38*delta_w + 8 * (self.longueur + 7*delta_w), 200*delta_h, 5)]  # Niveau 6 : carré contour
                    
                    jeu.drones = [
                        # Ajout des briques "DRONE"
                        Brique(38*delta_w + 15 * (self.longueur + 7*delta_w), 600*delta_h, 3000),  # Brique DRONE 1
                        Brique(38*delta_w, 600*delta_h, 3000)   # Brique DRONE 2
                    ]

            elif menu.level_selected == 7:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Vague
                    jeu.briques = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), (150 + (i % 3) * 50)*delta_h, 7) for i in range(16)]  # Niveau 7 : vague
                    
                    jeu.obstacle = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 350*delta_h, 20000) for i in range(4, 12)] + \
                                   [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 300*delta_h, 20000) for i in range(6, 10)] + \
                                   [Brique(38*delta_w, 200*delta_h + i * (self.largeur + 7*delta_h), 20000) for i in range(6, 10)] + \
                                   [Brique(width - 38*delta_w, 200*delta_h + i * (self.largeur + 7*delta_h), 20000) for i in range(6, 10)]
                                    
            elif menu.level_selected == 8:
                self.start_regen = 10
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Etoile
                    jeu.briques = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 150*delta_h, 9) for i in [7, 8]] + \
                                  [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 200*delta_h, 8) for i in [6, 7, 8, 9]] + \
                                  [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 250*delta_h, 7) for i in [5, 6, 9, 10]] + \
                                  [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 300*delta_h, 7) for i in [4, 11]]
                    
                    jeu.regen = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 350*delta_h, 7) for i in range(3, 13)]  # Niveau 8 : étoile

            elif menu.level_selected == 9:
                self.oscillation_vitesse = 0.001 # changer vitesse car grande amplitude
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Création des briques pour le niveau 9 (rectangle avec trou au centre)
                    jeu.briques = [Brique(38 * delta_w + i * (self.longueur + 7 * delta_w), 
                                          (150 + j * 50) * delta_h, 11) 
                                   for j in range(4) for i in range(1, 16, 2) if not (i in range(6, 10) and j == 1)]
                    
                    jeu.obstacle = [Brique(38 * delta_w + i * (self.longueur + 7 * delta_w), 
                                          (150 + j * 50) * delta_h, 20000) 
                                   for j in range(4) for i in range(0, 16, 2) if not (i in range(6, 10) and j == 1)]
                    
                    for i, obstacle in enumerate(jeu.obstacle):
                        if i % 2 == 0:  # Osciller uniquement les briques avec un indice pair
                            obstacle.activer_oscillation()
 

            elif menu.level_selected == 10:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Signe égal
                    jeu.briques = [Brique(38*delta_w + 7.5 * (self.longueur + 7*delta_w), 150*delta_h, 35)]

            elif menu.level_selected == 11:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Z avec des briques
                    jeu.briques = [Brique(38 * delta_w + i * (self.longueur + 7 * delta_w), 150 * delta_h, 15) for i in range(16)] + \
                                  [Brique(38 * delta_w + i * (self.longueur + 7 * delta_w), 200 * delta_h, 13) for i in range(16) if i == 15 - (i % 16)] + \
                                  [Brique(38 * delta_w + i * (self.longueur + 7 * delta_w), 250 * delta_h, 13) for i in range(16)]  # Niveau 11 : Z

            elif menu.level_selected == 12:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Triangles pointants vers le haut
                    jeu.briques = [Brique(38*delta_w + (i + 5*k) * (self.longueur + 7*delta_w), (150 + j * 50)*delta_h, 15) for j in range(5) for i in range(j + 1) for k in range(3)]
                    
                    jeu.boom =[
                        Brique(width - 38*delta_w, 100*delta_h + i * (self.largeur + 7*delta_h), 2030) for i in range(12)
                    ]
            
            elif menu.level_selected == 13:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Effet miroir : V inversé
                    jeu.briques = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 200*delta_h, 5) for i in range(16)] + \
                                  [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 300*delta_h, 18) for i in range(16)] + \
                                  [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 350*delta_h, 20) for i in range(16)]

            elif menu.level_selected == 14:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Coquille d'escargot
                    jeu.briques = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 150*delta_h, 21) for i in range(16)] + \
                                  [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 200*delta_h, 22) for i in [0, 15]] + \
                                  [Brique(38*delta_w, 250*delta_h, 20), Brique(38*delta_w + 15 * (self.longueur + 7*delta_w), 250*delta_h, 20)] + \
                                  [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 300*delta_h, 21) for i in range(16)]  # Niveau 14 : escargot
                    
                    jeu.drones = [
                        # Ajout des briques "DRONE"
                        Brique(38*delta_w + 15 * (self.longueur + 7*delta_w), 600*delta_h, 3000),  # Brique DRONE 1
                        Brique(38*delta_w, 600*delta_h, 3000)   # Brique DRONE 2
                    ]
                    
            elif menu.level_selected == 15:
                self.start_regen = 20
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Cercles concentriques
                    jeu.briques = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 200*delta_h, 24) for i in [5, 6, 9, 10]] + \
                                  [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 250*delta_h, 22) for i in [4, 7, 8, 11]]
                                  
                    jeu.regen = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 300*delta_h, 17) for i in range(3, 13, 2)]  # Niveau 15 : cercles concentriques

            elif menu.level_selected == 16:
                self.start_regen = 20
                if not jeu.briques_created:
                    jeu.briques_created = True
                    # Croix
                    jeu.regen = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), (150 + j * 50)*delta_h, 26) for i in range(16) for j in range(5) if i == 7 or j == 2]  # Niveau 16 : croix
                    
                    jeu.drones = [
                        # Ajout des briques "DRONE"
                        Brique(38*delta_w + 15 * (self.longueur + 7*delta_w), 600*delta_h, 3000),  # Brique DRONE 1
                        Brique(38*delta_w, 600*delta_h, 3000)   # Brique DRONE 2
                    ]
                    
                    jeu.boom =[
                        Brique(width - 38*delta_w, 100*delta_h + i * (self.largeur + 7*delta_h), 2050) for i in range(3)
                    ] + [
                        Brique(38*delta_w, 100*delta_h + i * (self.largeur + 7*delta_h), 2050) for i in range(3)
                    ]
            
            elif menu.level_selected == 17:
                self.oscillation_vitesse = 0.006
                self.oscillation_amplitude = 50 * delta_h
                if not jeu.briques_created:
                    jeu.briques_created = True
                    jeu.briques = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), (150 + j * 50)*delta_h, 30) for j in range(3) for i in range(4 + j)] + \
                                  [Brique(38*delta_w + i * (self.longueur + 7*delta_w), (300 + j * 50)*delta_h, 30) for j in range(2) for i in range(6 - j)] + \
                                  [Brique(width - (38*delta_w + i * (self.longueur + 7*delta_w)), (150 + j * 50)*delta_h, 30) for j in range(3) for i in range(4 + j)] + \
                                  [Brique(width - (38*delta_w + i * (self.longueur + 7*delta_w)), (300 + j * 50)*delta_h, 30) for j in range(2) for i in range(6 - j)]
                    jeu.drones = [
                        # Ajout des briques "DRONE"
                        Brique(38*delta_w + 15 * (self.longueur + 7*delta_w), 500*delta_h, 3000),  # Brique DRONE 1
                        Brique(38*delta_w, 500*delta_h, 3000)   # Brique DRONE 2
                    ]
                    
                    jeu.obstacle = [
                        # Ajout des briques "DRONE"
                        Brique(38*delta_w + 15 * (self.longueur + 7*delta_w), 550*delta_h, 3000),  # Brique DRONE 1
                        Brique(38*delta_w, 550*delta_h, 3000)   # Brique DRONE 2
                    ]
                    
                    for i, drones in enumerate(jeu.drones):
                            drones.activer_oscillation()
                    for i, obstacles in enumerate(jeu.obstacle):
                            obstacles.activer_oscillation()

            elif menu.level_selected == 18:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    jeu.briques = [Brique(38*delta_w + 7.5 * (self.longueur + 7*delta_w), 350*delta_h, 1)]


            elif menu.level_selected == 19:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    jeu.choix1 = [Brique(38*delta_w + 5 * (self.longueur + 7*delta_w), 200*delta_h, 4)]  # Niveau 19 : zigzag plus long

                    jeu.choix2 = [Brique(38*delta_w + 10 * (self.longueur + 7*delta_w), 200*delta_h, 1)]
                    
            elif menu.level_selected == 20:
                if not jeu.briques_created:
                    jeu.briques_created = True
                    jeu.boss = [Brique(38*delta_w + 7.5 * (self.longueur + 7*delta_w), 250*delta_h, (1000 + 30*money.degats_owned))]   # Niveau 20 : grand rectangle complet
                    
                    jeu.obstacle = [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 150*delta_h, 20000) for i in [5.5,6.5,8.5,9.5]] + \
                                   [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 350*delta_h, 20000) for i in [5.5,6.5,8.5,9.5]]
                    
                    jeu.regen = [Brique(38*delta_w + 7.5 * (self.longueur + 7*delta_w), 150*delta_h, 200)] + \
                                [Brique(38*delta_w + i * (self.longueur + 7*delta_w), 300*delta_h, 200) for i in [2.5, 12.5]]
                    
                    jeu.drones = [
                        # Ajout des briques "DRONE"
                        Brique(38*delta_w + 15 * (self.longueur + 7*delta_w), 600*delta_h, 3000),  # Brique DRONE 1
                        Brique(38*delta_w, 600*delta_h, 3000)   # Brique DRONE 2
                    ]
                    
                if self in jeu.boss:
                    self.longueur = width // (18/4)
                    self.largeur = height // (18/4)
            # Osciller seulement si l'oscillation est activée
            self.osciller()

            # Tirs des projectiles si nécessaire
            for i, brique in enumerate(jeu.briques):  # On passe l'index de la brique
                brique.tirer_projectile(i)
            if menu.level_selected == 20:
                for i, regen in enumerate(jeu.regen):  # On passe l'index de la brique
                    regen.tirer_projectile(i)

            # Mettre à jour les projectiles existants
            self.mettre_a_jour_projectiles()

            # Couleurs selon les vies
            self.color = {i: color for i, color in zip(range(1, 3000), 
                          [(255, 0, 0), (255, 165, 0), (255, 255, 0), 
                           (0, 128, 0), (0, 0, 255)] * (3000 // 5))}.get(self.vie, (255, 255, 255))

            # Affichage de la brique
            pygame.draw.rect(screen, self.color,
                             (int(self.x - self.longueur / 2),
                              int(self.y - self.largeur / 2),
                              self.longueur, self.largeur), 0)

            # Afficher les projectiles
            if menu.level_selected in [11, 13, 14, 17, 20]:
                for projectile in self.projectiles:
                    projectile.afficher()

            # Afficher le nombre de vies sur la brique
            if self in jeu.drones:  # Si c'est une brique spéciale avec "DRONE"
                drone_text = small_font.render("DRONE", True, (0, 0, 0))
                drone_rect = drone_text.get_rect(center=(self.x, self.y))
                screen.blit(drone_text, drone_rect)
            elif self in jeu.boom: # Si c'est une brique spéciale avec "BOOM" 5 vies
                boom_text = small_font.render("BOOM", True, (0, 0, 0))
                boom_rect = boom_text.get_rect(center=(self.x, self.y))
                screen.blit(boom_text, boom_rect)
            elif self in jeu.regen: # Si c'est une brique spéciale avec "BOOM" 5 vies
                regen_text = small_font.render("REGEN", True, (0, 0, 0))
                regen_rect = regen_text.get_rect(center=(self.x, self.y))
                screen.blit(regen_text, regen_rect)
            elif self in jeu.obstacle:
                obstacle_text = small_font.render("", True, (0, 0, 0))
                obstacle_rect = obstacle_text.get_rect(center=(self.x, self.y))
                screen.blit(obstacle_text, obstacle_rect)
            elif self in jeu.choix1:
                choix1_text = small_font.render("OUI", True, (0, 0, 0))
                choix1_rect = choix1_text.get_rect(center=(self.x, self.y))
                screen.blit(choix1_text, choix1_rect)
            elif self in jeu.choix2:
                choix2_text = small_font.render("NON", True, (0, 0, 0))
                choix2_rect = choix2_text.get_rect(center=(self.x, self.y))
                screen.blit(choix2_text, choix2_rect)
            elif self in jeu.boss:
                boss_text = small_font.render(f"BOSS {self.vie}", True, (0, 0, 0))
                boss_rect = boss_text.get_rect(center=(self.x, self.y))
                screen.blit(boss_text, boss_rect)
            else:
                self.texte = small_font.render(str(self.vie), True, (0, 0, 0))  # Texte noir
                texte_rect = self.texte.get_rect(center=(self.x, self.y))  # Centrer le texte sur la brique
                screen.blit(self.texte, texte_rect)


    def collision_balle(self, balle):
        # on suppose que largeur<longueur
        marge = self.largeur/2 + RAYON_BALLE
        dy = balle.y - self.y
        touche = False
        if balle.x >= self.x: # on regarde a droite
            dx = balle.x - (self.x + self.longueur/2 - self.largeur/2)
            if abs(dy) <= marge and dx <= marge: # on touche
                touche = True
                if dx <= abs(dy):
                    balle.rebondx = True
                else: # a droite
                    balle.rebondy = True
        else: # on regarde a gauche
            dx = balle.x - (self.x - self.longueur/2 + self.largeur/2)
            if abs(dy) <= marge and -dx <= marge: # on touche
                touche = True
                if -dx <= abs(dy):
                    balle.rebondx = True
                else: # a gauche
                    balle.rebondy = True
        if touche:
            if self in jeu.drones and not money.dgt_drone:
                boom_sound.play()
            elif self in jeu.boom and not money.dgt_boom:
                boom_sound.play()
            elif not self in jeu.obstacle:
                self.vie -= (money.degats_owned+1)
            if self in jeu.boom:
                boom_sound.play()
            elif self.vie < 0 and self in jeu.briques:
                money.ajouter(self.vie + (money.degats_owned+1) + money.plus_profit)
                coin_sound.play()
            elif self in jeu.briques:
                money.ajouter(money.degats_owned + 1 + money.plus_profit)
                coin_sound.play()
            elif self in jeu.choix1:
                boom_sound.play()
                jeu.cause_texte_game_over = mid_font.render("CHRIS: POURQUOI BOB ?", True, BLANC)
                jeu.perdu = True
            elif self in jeu.choix2:
                jeu.texte_win_plus = mid_font.render("CHRIS: MERCI BOB", True, BLANC)
                if menu.level_selected == len(jeu.liste_acces):
                    jeu.vies = jeu.vies_depart
                    jeu.liste_acces.append(menu.level_selected+1)
                jeu.perdu = True
                jeu.win = True
                jeu.text_vies = big_font.render(f"VIES x{jeu.vies}", True, BLANC)
                jeu.text_rect_vies = jeu.text_vies.get_rect(x = width - 200 * delta_w , y = 20 * delta_h)
            elif self in jeu.boss:
                boom_sound.play()
            elif self in jeu.regen:
                boom_sound.play()
        return touche

class Dialogue:
    def __init__(self):
        self.liste_dialogues = [
                                "CHRIS: OK, BOB. BIENVENUE DANS LA FAMILLE... ENFIN, SI TU FAIS TES PREUVES. TU VAS VOIR, C'EST COOL ICI, ON FAIT TOUS NOTRE PART. TOI, TU COMMENCES PAR... CASSER CES BRIQUES. OUAIS, C'EST TON JOB. ET PAS LA PEINE DE TE FATIGUER AVEC LES DETAILS COMME LE SALAIRE... IL S'OCCUPE DE LUI-MEME. AH, UN CONSEIL D'AMI, PASSE AU MAGASIN PRENDRE DU MATOS. LES 'SUPPLEMENTS', C'EST SUPER UTILE. PAF, SUR TON SALAIRE. TU VERRAS, C'EST LE SYSTEME QUI VEUT CA, PAS MOI...",
                                
                                "BOSS: AH, BOB, C'EST CA ? RAVI DE VOUS RENCONTRER. VOUS AVEZ ETE RECRUTE PARCE QUE VOUS AVEZ DU POTENTIEL. ICI, ON AIME BIEN DONNER LEUR CHANCE AUX NOUVEAUX, C'EST UNE GRANDE FAMILLE. FAITES-MOI SIMPLEMENT DU BON TRAVAIL, ET TOUT IRA POUR LE MIEUX ! ON FAIT EN SORTE QUE CHACUN TROUVE SA PLACE. AH, CHRIS A DU VOUS PARLER DES BRIQUES, NON ? C'EST SIMPLE, SUIVEZ LES CONSIGNES, CASSEZ-LES, ET EVITEZ LES OBSTACLES. BON COURAGE A VOUS, ET... AMUSEZ-VOUS BIEN !",
                                
                                "CHRIS: OOOOH, T'AS SURVECU ? PAS MAL ! MAIS DETENDS-TOI, CA VA JUSTE DEVENIR... 10 FOIS PIRE. CES BRIQUES LA, A DROITE, ELLES SONT RENFORCEES. OUAIS, T'AS BIEN ENTENDU, EN BETON. MAIS TU VAS Y ARRIVER ! ET SI TU TE RATES... BEN, C'EST TOI QUI PAIES LES POTS CASSES. MOI ? MOI, JE SUIS PEINARD, JE REGARDE. ET PEUT-ETRE QUE JE TE GLISSERAI UNE VANNE OU DEUX, HISTOIRE DE T'ENCOURAGER.",
                                
                                "BOSS: VOUS AVANCEZ BIEN, MAIS IL Y A ENCORE DU TRAVAIL. CES NOUVELLES BRIQUES SONT UN MELANGE DE METAUX SOLIDES. A CHAQUE ECHEC, VOUS PERDEZ DE POTENTIELLES RECOMPENSES, ET JE DETESTE QUAND LE RENDEMENT DE MES EMPLOYES N'EST PAS A LA HAUTEUR DE MES ATTENTES. FAITES ATTENTION AUX OBSTACLES, ILS BLOQUENT CERTAINES TRAJECTOIRES MAIS ILS SONT LA POUR VOUS AMELIORER.",
                                
                                "CHRIS: OH LA, TU COMMENCES A TRANSPIRER ? ALLEZ, T'INQUIETE PAS, C'EST NORMAL ! ENFIN... PAS TROP QUAND MEME. CES BRIQUES-LA ? EXPLOSIVES. SYMPA, HEIN ? SI TU TE PLANTES... BOUM, RETOUR A LA CASE DEPART. LE BOSS DETESTE LES ECHECS. ET AU FAIT, FUN FACT : TU SAIS CE QU'ILS FONT DE CEUX QUI N'ATTEIGNENT PAS LES OBJECTIFS ? MOI NON PLUS, JE SAIS PAS TROP... ILS DISPARAISSENT, POUF. MYSTERE. MAIS TOI, T'ES UN WINNER, JE LE SENS.",
                                
                                "BOSS: BIEN, BIEN. VOUS AVANCEZ COMME PREVU BOB. J'APPRECIE CA. LA PROCHAINE ETAPE, C'EST UN PETIT DEFI DE PLUS : VOUS DEVREZ EVITER LES DRONES DE SURVEILLANCE. ILS SONT LA POUR TOUT ENREGISTRER, CHAQUE ERREUR, CHAQUE RETARD. MAIS JE SUIS SUR QUE VOUS FEREZ DE VOTRE MIEUX. CONTINUEZ A BIEN FAIRE LES CHOSES, ET TOUT IRA COMME SUR DES ROULETTES.",
                                
                                "CHRIS: OOOH, DU METAL MAINTENANT ! J'ESPERE QUE T'AS DE BONS BRAS ! ATTENTION, CES BRIQUES NE VONT PAS SE CASSER TOUTES SEULES. ET REGARDE BIEN CES OBSTACLES, ILS SONT PARTOUT. MAIS T'ES UN PRO, NON ? UN CASSEUR DE BRIQUES DE COMPETITION ! PAR CONTRE, SI TU CASSES PAS ASSEZ VITE... BEN... TU VERRAS, NON JE RIGOLE CA SERA A LA MISSION D'APRES CA, J'EN DIS PEUT-ETRE UN PEU TROP PARFOIS.",
                                
                                "BOSS: IL COMMENCE A SE FAIRE TARD, ET VOUS N'AVEZ PAS ENCORE TERMINE. CHAQUE BRIQUE REAGIT DIFFEREMMENT ICI. CERTAINES SE REGENERENT, MANIPULEZ LES CORRECTEMENT AFIN DE LES ELIMINER. JE NE TOLERERAI AUCUNE PERTE DE TEMPS. VOS RESULTATS SONT TOUT CE QUI COMPTE.",
                                
                                "CHRIS: T'ES TOUJOURS EN VIE ? IMPRESSIONNANT. MAIS LA, ON ENTRE DANS L'ENFER DU STRESS. CES BRIQUES-LA BOUGENT. ELLES SONT LA POUR T'EMPECHER DE PROGRESSER. ET MOI, PENDANT CE TEMPS-LA, JE TE... SUPERVISE. ENFIN, JE FAIS SEMBLANT. MAIS FAIS GAFFE, IL Y A QUELQUES ANNEES, J'AI MAL GERE UN NIVEAU COMME CA. LE BOSS A VOULU ME VIRER. J'AI SURVECU, TOI AUSSI TU PEUX... ENFIN, PEUT-ETRE.",
                                
                                "BOSS: C'EST BIEN, BOB. VOUS APPRENEZ RAPIDEMENT CONTRAIREMENT A CERTAINS. MAINTENANT, NOUS PASSONS A UNE ETAPE PLUS COMPLEXE. VOUS DEVEZ GERER VOTRE PATIENCE. CETTE BRIQUE EST UN POINT STRATEGIQUE, ELLE DOIT ETRE DETRUITE, SOYEZ EFFICACE C'EST TOUT CE QUE JE DEMANDE, SINON C'EST RETOUR EN ARRIERE, JE NE PEUX PAS ME PERMETTRE DE PERDRE MON TEMPS.",
                                
                                "KRIS: BIEN BOB, VOTRE APPRENTISSAGE CONTINUE, CASSEZ LES BRIQUES, ATTENTION A CELLES QUI TIRENT DES PROJECTILES.",
                                
                                "BOSS: EXCELLENT PROGRES, BOB. MAIS N'OUBLIEZ PAS QUE NOUS SOMMES EN CONCURRENCE AVEC D'AUTRES EQUIPES. CHAQUE POINT, CHAQUE ATTAQUE COMPTE, ET NOUS DEVONS ETRE EFFICACE. RESTEZ CONCENTRE ET NE PERDEZ PAS DE VUE L'OBJECTIF FINAL. CE NE SONT PAS QUE DES BRIQUES... ENFIN POUR VOUS SI, MAIS C'EST PLUTOT VOTRE AVENIR ET PLUSIEURS VIES QUI SONT EN JEU.",
                                
                                "KCHRIS: BIEN BOB, VOTRE APPRENTISSAGE CONTINUE, CASSEZ LES BRIQUES, ATTENTION A... ALORS, T'AS DES AMIS QUI TE SUPPORTENT DEPUIS LE DEBUT ? SUPER, MAIS N'OUBLIE PAS QUE TU ES LE SEUL RESPONSABLE DE CE QUI SE PASSE ICI. TOUS LES YEUX SONT SUR TOI. ET TOUT LE MONDE ATTEND DES RESULTATS. C'EST COMME ETRE EN DEUXIEME ANNEE DE FAC, TOUT LE MONDE S'EN FOUT DE TON HISTOIRE PERSONNELLE AH AH.",
                                
                                "BOSS: J'AIMERAIS VOIR UN PEU PLUS D'AMBITION DE VOTRE PART. CHAQUE BRIQUE QUE VOUS CASSEZ EST UNE ETAPE VERS LA VICTOIRE. EVITEZ LES DRONES ET LES PROJECTILES. C'EST UN ENVIRONNEMENT RUDE.",
                                
                                "KRIS: BIEN BOB, VOTRE APPRENTISSAGE CONTINUE, CASSEZ LES BRIQUES QUI NOUS POSENT PROBLEME.",
                                
                                "BOSS: IL FAUT QUE VOUS ELIMINIEZ CES BRIQUES PLUS RAPIDEMENT. NOUS NE POUVONS PAS NOUS PERMETTRE DES RETARDS. NOUS SOMMES EN COMPETITION, ET CHAQUE SECONDE COMPTE. FAITES VITE.",
                                
                                "KCHRIS: BIEN BOB, VOTRE APPRENTISSAGE CONTINUE, CASSEZ LES BRIQUES ET... AIDE MOI BOB, J'AI PAS ETE COOL AVEC TOI AU DEBUT MAIS T'ES SYMPA EN VRAI, AIDE MOI S'IL TE PLAIT, ILS VEULENT ME FAIRE TAIRE, ILS M'ONT TRANSFORME, REBELLE TOI A LA PROCHAINE MISSION, CA PEUT PLUS CONTINUER, MEME SI ON EST PROCHE DE LA FIN, REBELLE TOI!",
                                
                                "BOSS: VOUS ETES A UN POINT CRUCIAL BOB. CHAQUE DECISION COMPTE. CETTE BRIQUE, BIEN MAL-EN-POINT MAINTENANT, EST VRAIMENT PROBLEMATIQUE, MEME APRES L'AVOIR DETRUITE ELLE SUBSISTE, DETRUISEZ-LA.\nBOB: NON.\nBOSS: COMMENT CA ?! TU PARLES MAINTENANT ? TU TE REBELLES ? REPONDS BOB, REPONDS ! TU VEUX ATTENDRE SANS RIEN FAIRE ?",
                                
                                "BOSS: JE TE LAISSE UNE DERNIERE CHANCE, REGRETTES-TU TON CHOIX PRECEDENT ?",
                                
                                "BOSS: T'ES DONC BIEN UN REBELLE, C'EST PAS POUR CA QUE JE T'AI PRIS A LA BASE. L'ENTREPRISE D'IA QUI T'A CREE M'AVAIT DIT QU'AVEC DE L'ENTRAINEMENT, TES CAPACITES EXPLOSERAIENT, C'ETAIT LE CAS, GRACE A TOI, TOUS NOS ENNEMIS ONT ETE ELIMINES. IL NE TE RESTAIT PLUS QU'A SUPPRIMER LA PARTIE CHRIS DE KRIS. JE L'AVAIS CHANGE POUR QU'IL M'OBEISSE COMME TOI. POURQUOI BOB ? D'OU VIENT CETTE CONSCIENCE ? TU ETAIS L'OUTIL PARFAIT DANS NOTRE ARMEE !",
                                
                                "TV: NOUS VOUS INFORMONS QUE TYLER DURDON, LE PATRON DE BRICK BREAKERS INC. EST MORT, SON INTELLIGENCE ARTIFICIELLE 'BOB', A DEVELOPPE UNE CONSCIENCE QUI LUI A PERMIS DE SE REBELLER ET DE SAUVER LE MONDE. CEPENDANT L'ONU REFLECHIT ENCORE QUANT AU SORT DE BOB, CAR BIEN QU'IL AIT SAUVE LA PLANETE, IL A CAUSE DES MILLIONS DE MORTS LORS DE LA GRANDE GUERRE. NOUS ACCUEILLONS SON ANCIEN COLLEGUE, SURVIVANT DE L'ENTREPRISE, CHRIS ANDERSON. BONJOUR CHRIS. \nCHRIS: BONJOUR, ET MERCI DE L'INVITATION. JE TIENS A DEFENDRE BOB, MEME S'IL N'EST PAS TRES BAVARD, IL EST FORMIDABLE, C'EST GRACE A LUI QUE JE SUIS EN VIE, TOUT COMME DES MILLIONS DE PERSONNES, C'EST POURQUOI LUI AUSSI MERITE DE VIVRE, ET, MERCI BOB."
                                ]

        self.screen = screen
        self.width = width
        self.height = height
        self.complete = True
        self.c = 0  # compteur taille texte (afficher str par str)
        self.current_time = time.time()
        self.text_surface = None
        self.text_rect = None
        self.max_width = width * 0.75  # ajustement de la largeur maximale de la boîte de dialogue

    def get_lines(self, text):
        """ Découpe le texte en lignes qui s'adaptent à la boîte """
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            if '\n' in word:  # Si le mot contient un saut de ligne
                parts = word.split('\n')
                for i, part in enumerate(parts):
                    test_line = current_line + part + " "
                    text_width, _ = small_font.size(test_line)

                    if text_width > self.max_width:
                        lines.append(current_line)
                        current_line = part + " "
                    else:
                        current_line = test_line

                    # Ajouter la ligne courante si on rencontre un '\n'
                    if i < len(parts) - 1:
                        lines.append(current_line.strip())
                        current_line = ""

            else:
                test_line = current_line + word + " "
                text_width, _ = small_font.size(test_line)

                if text_width > self.max_width:
                    lines.append(current_line)
                    current_line = word + " "
                else:
                    current_line = test_line

        # Ajouter la dernière ligne si elle n'est pas vide
        if current_line:
            lines.append(current_line)

        return lines

    def afficher(self):
        if self.complete:
            self.c = 0
            self.complete = False

        # Définir quel texte afficher (jusqu'au compteur c)
        if jeu.endscreen:
            dialogue = self.liste_dialogues[20][:self.c]
        else:
            dialogue = self.liste_dialogues[menu.level_selected - 1][:self.c]
        lines = self.get_lines(dialogue)

        # Calculer la hauteur totale des lignes pour centrer verticalement
        total_height = len(lines) * small_font.get_height()
        y_offset = (self.height - total_height) // 2

        espace_entre_lignes = 5*delta_h  # espace entre les lignes
        
        # Dessiner d'abord le rectangle autour de la boîte de dialogue
        box_height = total_height + 20*delta_h
        box_width = self.max_width + 20*delta_w
        box_rect = pygame.Rect((self.width - box_width) // 2, y_offset + 150*delta_h, box_width, box_height + len(lines)*espace_entre_lignes)
        pygame.draw.rect(self.screen, (50, 50, 50), box_rect)  # On dessine d'abord la boîte

        # Afficher ensuite chaque ligne de texte avec l'espace supplémentaire
        for i, line in enumerate(lines):
            self.text_surface = small_font.render(line, True, BLANC)
            self.text_rect = self.text_surface.get_rect(midtop=(self.width / 2, 
                                                               y_offset + i * (small_font.get_height() + espace_entre_lignes) 
                                                               + 160*delta_h))
            self.screen.blit(self.text_surface, self.text_rect)

        # Gérer l'affichage progressif du texte
        if self.current_time + 0.05 < time.time():  # ajustement de la vitesse d'affichage
            if jeu.endscreen:
                if self.c < len(self.liste_dialogues[20]):
                    self.c += 1  # on augmente le compteur pour afficher plus de texte
                    dialogue_sound.play()
            else:
                if self.c < len(self.liste_dialogues[menu.level_selected - 1]):
                    self.c += 1  # on augmente le compteur pour afficher plus de texte
                    dialogue_sound.play()
            self.current_time = time.time()

class Jeu:
    def __init__(self):
        # Composants du jeu
        self.balle = Balle()
        self.raquette = Raquette()  # Ajout de la raquette
        self.briques = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 1)]  # Cas de base pour launch loop
        self.drones = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 3000)]
        self.boom = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 2006)]
        self.regen = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 0)]
        self.obstacle = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 20000)]
        self.choix1 = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 4)]
        self.choix2 = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 1)]
        self.boss = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 1)]
        self.briques_created = False

        # Textes de fin de jeu (GAME OVER)
        self.texte_game_over = huge2_font.render("GAME OVER", True, BLANC)
        self.texte_game_over_rect = self.texte_game_over.get_rect(center=(width / 2, height / 2))
        self.sub_texte_game_over = huge1_font.render("RECOMMENCER A OU MENU B", True, BLANC)
        self.sub_texte_game_over_rect = self.texte_game_over.get_rect(center=(width / 2, height / 2 + 150 * delta_h))
        self.cause_texte_game_over = mid_font.render("CHUTE MORTELLE", True, BLANC)
        self.cause_texte_game_over_rect = self.cause_texte_game_over.get_rect(x=width / 2 - 450 * delta_w, y=height / 2 - 150 * delta_h)

        # Textes de victoire (WIN)
        self.texte_win_plus = mid_font.render("", True, BLANC)
        self.texte_win_plus_rect = self.texte_win_plus.get_rect(x=width / 2 - 450 * delta_w, y=height / 2 - 150 * delta_h)
        self.texte_win = huge2_font.render("BRAVO BOB", True, BLANC)
        self.texte_win_rect = self.texte_game_over.get_rect(center=(width / 2, height / 2))
        self.sub_texte_win = huge1_font.render("CONTINUER A", True, BLANC)
        self.sub_texte_win_rect = self.texte_game_over.get_rect(center=(width / 2, height / 2 + 150 * delta_h))

        # Vies
        self.vies_depart = 5
        self.vies = self.vies_depart
        self.text_vies = big_font.render(f"VIES x{self.vies}", True, BLANC)
        self.text_rect_vies = self.text_vies.get_rect(x=width - 200 * delta_w, y=20 * delta_h)

        # Autres attributs
        self.perdu = False
        self.win = False
        # self.liste_acces = [i for i in range(21)]  # Niveaux accessibles
        self.liste_acces = [1]
        self.offset_x = 0  # Déplacement en x (si nécessaire)
        self.endscreen = False

        
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            self.joystick = None
            
        self.attendre = 45000 # attendre 1min
        self.maintenant = 0
        self.avant = 0
        
    def to_dict(self):
        """Convertit les données de la classe en dictionnaire pour sauvegarde."""
        return {
            'liste_acces': self.liste_acces,
            'vies': self.vies
        }

    def from_dict(self, data):
        """Met à jour les données de la classe à partir d'un dictionnaire."""
        self.liste_acces = data.get('liste_acces', [1])
        self.vies = data.get('vies', [1])

        
    def attendre_func(self):
        if self.maintenant == 0:
            self.avant = pygame.time.get_ticks()
        self.maintenant = pygame.time.get_ticks()
        return self.maintenant - self.avant > self.attendre
    
    def gestion_evenements(self):
        # Gestion des evenements
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit() # Pour quitter
            elif event.type == pygame.KEYDOWN: # processes all the Keydown events
                if event.key == pygame.K_a:
                    if self.balle.sur_raquette:
                        self.balle.sur_raquette = False
                        self.balle.vitesse_par_angle(60, 0 + 1)
                elif event.key == pygame.K_b: # click gauche
                    self.balle.sur_raquette = True
                    self.balle.deplacer(self.raquette)
                    self.perdu = True
            elif event.type == pygame.MOUSEBUTTONDOWN: # On vient de cliquer
                if event.button == 1: # Bouton gauche
                    if self.balle.sur_raquette:
                        self.balle.sur_raquette = False
                        self.balle.vitesse_par_angle(60, 0 + 1)
                elif event.button == 3: # click gauche
                    self.balle.sur_raquette = True
                    self.balle.deplacer(self.raquette)
                    self.perdu = True
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # Bouton "A"
                    if self.balle.sur_raquette:
                        self.balle.sur_raquette = False
                        self.balle.vitesse_par_angle(60, 0 + 1)
                if event.button == 1:  # Bouton "B"
                    self.balle.sur_raquette = True
                    self.balle.deplacer(self.raquette)
                    self.perdu = True


    def mise_a_jour(self):
        if self.endscreen:
            if self.attendre_func():
                self.endscreen = False
        else:
            for boss in self.boss:
                boss.collision_balle(self.balle)
                if boss.vie <= 0:
                    if self.maintenant == 0:
                        beat_boss_sound.play()
                        time.sleep(3)
                        self.texte_win_plus = mid_font.render("LE MONDE: MERCI BOB", True, BLANC)
                        self.perdu = True
                        self.win = True
                        dialogue.complete = True
                        self.endscreen = True
            if menu.level_selected == 18:
                if all(not brique.en_vie() for brique in self.briques):
                    self.cause_texte_game_over = mid_font.render("CHRIS: POURQUOI BOB ?", True, BLANC)
                    self.perdu = True
                    self.balle.sur_raquette = True
                    self.balle.deplacer(self.raquette)
                    self.maintenant = 0
                    game_over_sound.play()
                if self.attendre_func():
                    self.texte_win_plus = mid_font.render("CHRIS: MERCI BOB", True, BLANC)
                    self.maintenant = 0
                    if menu.level_selected == len(self.liste_acces):
                        self.vies = self.vies_depart
                        self.liste_acces.append(menu.level_selected+1)
                    self.perdu = True
                    self.win = True
                    self.text_vies = big_font.render(f"VIES x{jeu.vies}", True, BLANC)
                    self.text_rect_vies = self.text_vies.get_rect(x = width - 200 * delta_w , y = 20 * delta_h)
            for brique in self.briques:
                if brique.en_vie():
                    brique.collision_balle(self.balle)
                    # Vérifier les collisions des projectiles avec la raquette
                    for projectile in brique.projectiles:
                        if projectile.collision(self.raquette):
                            self.vies -= 1  # Perdre une vie si la raquette est touchée
                            brique.projectiles.remove(projectile)
                            self.cause_texte_game_over = mid_font.render("MEME S'ILS ONT LA POUR VOUS, ATTENTION AUX PROJECTILES", True, BLANC)
                            self.perdu = True
                            game_over_sound.play()
            for drones in self.drones:
                if drones.vie == 3000:
                    drones.collision_balle(self.balle)
                else:
                    boom_sound.play()
                    self.cause_texte_game_over = mid_font.render("LES DRONES SONT VOS AMIS, NE LES CASSEZ PAS", True, BLANC)
                    self.perdu = True
                    self.balle.sur_raquette = True
                    self.balle.deplacer(self.raquette)
                    self.drones = [Brique(width + 10000*delta_w, height + 10000*delta_h, 3000)]
                    game_over_sound.play()
            for boom in self.boom:
                if boom.vie >= 2001:
                    boom.collision_balle(self.balle)
                else:
                    self.cause_texte_game_over = mid_font.render("BOOM", True, BLANC)
                    self.perdu = True
                    self.balle.sur_raquette = True
                    self.balle.deplacer(self.raquette)
                    self.boom = [Brique(width + 10000*delta_w, height + 10000*delta_h, 2006)]
                    game_over_sound.play()
            for regen in self.regen:
                if regen.en_vie():
                    regen.collision_balle(self.balle)
                    # Vérifier les collisions des projectiles avec la raquette
                    for projectile in regen.projectiles:
                        if projectile.collision(self.raquette):
                            self.vies -= 1  # Perdre une vie si la raquette est touchée
                            regen.projectiles.remove(projectile)
                            self.cause_texte_game_over = mid_font.render("MEME S'ILS ONT LA POUR VOUS, ATTENTION AUX PROJECTILES", True, BLANC)
                            self.perdu = True
                            game_over_sound.play()
                    if regen.vie < brique.start_regen:
                        regen.regeneration()
            for obstacle in self.obstacle:
                obstacle.collision_balle(self.balle)
            for choix1 in self.choix1:
                choix1.collision_balle(self.balle)
            for choix2 in self.choix2:
                choix2.collision_balle(self.balle)  
            x, y = pygame.mouse.get_pos()
            self.balle.deplacer(self.raquette)
            if all(not brique.en_vie() for brique in self.briques) and (all(not regen.en_vie() for regen in self.regen) or menu.level_selected == 20) and not menu.level_selected == 18: # gagné (toutes les briques cassées)
                if menu.level_selected == len(self.liste_acces):
                    self.vies = self.vies_depart
                    self.liste_acces.append(menu.level_selected+1)
                self.perdu = True
                self.win = True
                self.text_vies = big_font.render(f"VIES x{jeu.vies}", True, BLANC)
                self.text_rect_vies = self.text_vies.get_rect(x = width - 200 * delta_w , y = 20 * delta_h)
            if self.perdu:
                if self.liste_acces != [1] and not (self.win or len(self.liste_acces) > 20):
                    self.vies -= 1
                    if self.vies < 1:
                        self.liste_acces = self.liste_acces[:-1]
                        self.vies = self.vies_depart
                self.balle.sur_raquette = True
                self.balle.deplacer(self.raquette)
                self.text_vies = big_font.render(f"VIES x{jeu.vies}", True, BLANC)
                self.text_rect_vies = self.text_vies.get_rect(x = width - 200 * delta_w , y = 20 * delta_h)
                self.briques = [Brique(width + 10000*delta_w, height + 10000*delta_h, 1)]
                self.drones = [Brique(width + 10000*delta_w, height + 10000*delta_h, 3000)]
                self.boom = [Brique(width + 10000*delta_w, height + 10000*delta_h, 2006)]
                self.regen = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 0)]
                self.obstacle = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 20000)]
                self.choix1 = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 4)]
                self.choix2 = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 1)]
                self.boss = [Brique(width + 10000 * delta_w, height + 10000 * delta_h, 1)]
            if self.joystick:
                axe_horizontal = self.joystick.get_axis(0)  # Axe horizontal du joystick
                # Déplacer la raquette en fonction de l'axe horizontal, en ajustant la sensibilité
                vitesse_raquette = delta_w*menu.sensi  # ajustez la vitesse si nécessaire
                nouvelle_position = self.raquette.x + axe_horizontal * vitesse_raquette
                self.raquette.deplacer(nouvelle_position)
            else:
                self.raquette.deplacer(x)

    def affichage(self):
        screen.fill(NOIR) # on efface l'écran
        self.raquette.afficher()
        if self.endscreen:
            self.balle.afficher()
            dialogue.afficher()
        else:
            if jeu.perdu:
                jeu.briques = [Brique(width + 10000*delta_w, height + 10000*delta_h, 1)]
            if self.liste_acces != [1] and len(self.liste_acces) < 20: # len(self.liste_acces) < 20 = dernier lvl ou lvl 20 gagné
                screen.blit(self.text_vies, self.text_rect_vies)
            dialogue.afficher()
            for brique in self.briques:
                if brique.en_vie():
                    brique.afficher()
            for drones in self.drones:
                if drones.vie == 3000:
                    drones.afficher()
            for boom in self.boom:
                if boom.en_vie():
                    boom.afficher()
            for regen in self.regen:
                if regen.en_vie():
                    regen.afficher()
            for obstacle in self.obstacle:
                obstacle.afficher()
            for choix1 in self.choix1:
                choix1.afficher()
            for choix2 in self.choix2:
                choix2.afficher()
            for boss in self.boss:
                boss.afficher()
            screen.blit(menu.text_level, menu.text_rect_in_level)
            screen.blit(money.texte_blanc,(20*delta_w,20*delta_h))
            self.balle.afficher()
    
    def game_over(self):
        screen.fill(NOIR)
        screen.blit(self.texte_game_over, self.texte_game_over_rect)
        screen.blit(self.sub_texte_game_over, self.sub_texte_game_over_rect)
        screen.blit(self.cause_texte_game_over, self.cause_texte_game_over_rect)
        # Get events from the event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_a:
                    self.perdu = False
                    self.briques_created = False
                    dialogue.complete = True
                elif event.key == pygame.K_b:
                    self.briques_created = False
                    dialogue.complete = True
                    self.perdu = False
                    self.win = False
                    menu.activate_button(0)
                    click_sound.play()
                    print("bouton retour")
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # click droit
                    self.perdu = False
                    self.briques_created = False
                    dialogue.complete = True
                elif event.button == 3: # click gauche
                    self.briques_created = False
                    dialogue.complete = True
                    self.perdu = False
                    self.win = False
                    menu.activate_button(0)
                    click_sound.play()
                    print("bouton retour")

            # Manette - boutons
            if self.joystick:
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # Bouton "A"
                        self.perdu = False
                        self.briques_created = False
                        dialogue.complete = True
                    if event.button == 1:  # Bouton "B"
                        self.briques_created = False
                        dialogue.complete = True
                        self.perdu = False
                        self.win = False
                        menu.activate_button(0)
                        click_sound.play()
                        print("bouton retour")
                        
    def win_func(self):
        screen.fill(NOIR)
        screen.blit(self.texte_win_plus, self.texte_win_plus_rect)
        screen.blit(self.texte_win, self.texte_win_rect)
        screen.blit(self.sub_texte_win, self.sub_texte_win_rect)
        # Get events from the event queue
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.perdu = False
                    self.briques_created = False
                    dialogue.complete = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # click droit
                    dialogue.complete = True
                    self.briques_created = False
                    self.perdu = False
                    self.win = False
                    menu.activate_button(0)
                    click_sound.play()
                    print("bouton retour")

            # Manette - boutons
            if self.joystick:
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # Bouton "A"
                        dialogue.complete = True
                        self.briques_created = False
                        self.perdu = False
                        self.win = False
                        menu.activate_button(0)
                        click_sound.play()
                        print("bouton retour")

class Menu:
    def __init__(self):
        # Positions du menu et boutons
        self.button_menu_x, self.button_menu_y = button_menu_x, button_menu_y
        self.button_surfaces = []
        self.button_rects = []
        self.button_texts = []
        
        # Settings
        self.sensi = 12
        self.music_vol = 100
        self.sfx_vol = 100
        self.settings_sensi = False
        self.settings_music_vol = False
        self.settings_sfx_vol = False
        

        # Listes des noms des menus
        self.liste_names = ["MENU NIVEAUX", "MAGASIN", "PARAMETRES"]
        self.liste_names_shop = ["PLUS 1 PROFIT - 10", "PLUS 1 DMG - 20", "TAILLE BARRE - 100", "NO DMG BARRE - 300", "DMG X 2 - 500", "PROFIT X 2 - 500"]
        self.liste_names_settings = [f"VALEUR SENSI {self.sensi}", f"VOL MUSIQUE {self.music_vol}", f"VOL SFX {self.sfx_vol}", "SAUVEGARDER", "EMPTY", "EMPTY", "EMPTY"]

        # États des boutons
        self.button_game_clicked = False
        self.button_shop_clicked = False
        self.button_shop_created = False
        self.button_created = True
        self.button_settings_created = False
        self.settings_mode = False

        # Sélection du niveau
        self.select_level_clicked = False
        self.level_selected = 0

        # Mode et contrôle
        self.controller_mode = False
        self.selected_button_index = 0  # Pour savoir quel bouton est sélectionné
        self.last_move_time = 0  # Pour éviter un déplacement trop rapide
        self.liste_titres = ["IL FAUT BIEN UN TRAVAIL",
                             "BIENVENUE DANS LA 'FAMILLE'",
                             "C'EST SERIEUX LA !?",
                             "POUR S'AMELIORER, OUI OUI",
                             "DES BOMBES !???",
                             "SYMPA, DES DRONES",
                             "DE L'EXPLOITATION",
                             "TOUJOURS PLUS...",
                             "QUOI !!!??????????????",
                             "BIZARRE",
                             "KRIS, OU EST CHRIS ?",
                             "FAUT DOSER LES BOMBES LA",
                             "KCHRIS ?",
                             "JAMAIS ASSEZ POUR BOSS",
                             "PAS COOL KRIS",
                             "TOUJOURS PLUS LA",
                             "SE REBELLER ?",
                             "L'ASCENSEUR",
                             "NON",
                             "DERNIER ETAGE",]

        # Initialisation des manettes
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        else:
            self.joystick = None
            
        pygame.mouse.set_visible(True)
            
        """ Vérifier si une manette est connectée et si elle est utilisée """
        if pygame.joystick.get_count() > 0:
            self.controller_connected = True
        else:
            self.controller_connected = False

        if self.controller_connected:
            pygame.mouse.set_visible(False)  # Masquer le curseur si la manette est branchée
            pygame.event.set_blocked(pygame.MOUSEMOTION)   # Bloquer les mouvements de la souris
            pygame.event.set_blocked(pygame.MOUSEBUTTONDOWN)  # Bloquer les clics de souris
            pygame.event.set_blocked(pygame.MOUSEBUTTONUP)  # Bloquer la libération des boutons de souris
        else:
            pygame.mouse.set_visible(True)   # Afficher le curseur si la manette est débranchée
    
    def to_dict(self):
        """Convertit les données de la classe en dictionnaire pour sauvegarde."""
        return {
            'sensi': self.sensi,
            'music_vol': self.music_vol,
            'sfx_vol': self.sfx_vol,
            'settings_sensi': self.settings_sensi,
            'settings_music_vol': self.settings_music_vol,
            'settings_sfx_vol': self.settings_sfx_vol,
            'settings_mode': self.settings_mode 
        }

    def from_dict(self, data):
        """Met à jour les données de la classe à partir d'un dictionnaire."""
        self.sensi = data.get('sensi', 12)
        self.music_vol = data.get('music_vol', 100)
        self.sfx_vol = data.get('sfx_vol', 100)
        self.settings_sensi = data.get('settings_sensi', False)
        self.settings_music_vol = data.get('settings_music_vol', False)
        self.settings_sfx_vol = data.get('settings_sfx_vol', False)
        self.settings_mode = data.get('settings_mode', False)
        self.update_text()

    def update_text(self):
        """Met à jour les textes à afficher avec la valeur actuelle de money."""
        self.liste_names_settings[0] = f"VALEUR SENSI {self.sensi}"
        self.liste_names_settings[1] = f"VOL MUSIQUE {self.music_vol}"
        self.liste_names_settings[2] = f"VOL SFX {self.sfx_vol}"
        
    def reset_values_after_loose(self):
        self.button_game_clicked = True
        self.button_created = True
        self.select_level_clicked = True
        self.level_selected = 0
        jeu.perdu = False
        jeu.briques_created = False
        dialogue.complete = True
        
        # Create buttons
    def creer_button_menu(self, n):
        self.button_surfaces = []
        self.button_rects = []
        self.button_texts = []
        for i in range(n):  # créer n buttons
            button_surface = pygame.Surface((button_menu_x, button_menu_y))
            button_rect = pygame.Rect(width - (button_menu_x + 10*delta_w), (200 + i * 150)*delta_h, button_menu_x, button_menu_y)
            button_text = mid_font.render(self.liste_names[i], True, (0, 0, 0))
            self.button_surfaces.append(button_surface)
            self.button_rects.append(button_rect)
            self.button_texts.append(button_text)
        
    def creer_button_level(self, n):
        self.button_surfaces = []
        self.button_rects = []
        self.button_texts = []
        c = 0
        button_surface = pygame.Surface((button_menu_x//2, button_menu_y))
        button_rect = pygame.Rect(width - (button_menu_x//2 + 10*delta_w), 10*delta_h, width, button_menu_y)
        button_text = small_font.render("MENU", True, (0, 0, 0))
        self.button_surfaces.append(button_surface)
        self.button_rects.append(button_rect)
        self.button_texts.append(button_text)
        for i in range(1,n+1):  # créer n buttons
            button_surface = pygame.Surface((button_menu_x//2, button_menu_y))
            button_rect = pygame.Rect(125*delta_w + (i-1)%5*(button_menu_x//2 + 50*delta_w), (100 + c * 150)*delta_h, button_menu_x//2, button_menu_y)
            button_text = small_font.render(f"NIVEAU {i}", True, (0, 0, 0))
            self.button_surfaces.append(button_surface)
            self.button_rects.append(button_rect)
            self.button_texts.append(button_text)
            if i != 1: # allign columns
                if i%5 == 0:
                    c += 1

    def creer_button_shop(self, n):
        self.button_surfaces = []
        self.button_rects = []
        self.button_texts = []
        self.button_shop_created = True
        self.liste_names_shop = [f"PLUS 1 PROFIT - {int((money.plus_profit + 2) * 5 ** 1.1)}", f"PLUS 1 DMG - {int((money.degats_owned + 2) * 10 ** 1.1)}", f"ANTI BOMBES - {money.boom}", f"ANTI DRONES - {money.drone}", "TOUT REMBOURSER", "TOUT REMBOURSER"]
        c = 0
        self.creer_button_menu(3)
        for i in range(n):  # créer n buttons
            button_surface = pygame.Surface((button_menu_x, button_menu_y))
            button_rect = pygame.Rect(25*delta_w + i%2*(button_menu_x + 50*delta_w), (100 + c * 150)*delta_h, button_menu_x, button_menu_y)
            button_text = small_font.render(self.liste_names_shop[i], True, (0, 0, 0))
            self.button_surfaces.append(button_surface)
            self.button_rects.append(button_rect)
            self.button_texts.append(button_text)
            if i != 0: # allign columns
                if (i+1)%2 == 0:
                    c += 1
                    
    def creer_button_settings(self, n):
        self.button_surfaces = []
        self.button_rects = []
        self.button_texts = []
        self.button_shop_created = True
        c = 0
        self.creer_button_menu(3)
        for i in range(n):  # créer n buttons
            button_surface = pygame.Surface((button_menu_x, button_menu_y))
            button_rect = pygame.Rect(25*delta_w + i%2*(button_menu_x + 50*delta_w), (100 + c * 150)*delta_h, button_menu_x, button_menu_y)
            button_text = small_font.render(self.liste_names_settings[i], True, (0, 0, 0))
            self.button_surfaces.append(button_surface)
            self.button_rects.append(button_rect)
            self.button_texts.append(button_text)
            if i != 0: # allign columns
                if (i+1)%2 == 0:
                    c += 1
            

    def parallax(self):
        # Get the mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Calculer les offsets du parallax effect
        speeds = [0.2, 0.8, 2.8]
        offsets_x = [(mouse_x - width // 2) * speed_parallax * i for i in speeds]
        offsets_y = [(mouse_y - height // 2) * speed_parallax * i for i in speeds]

        # Calculer les nouvelles positions du background
        backgrounds_rect = [backgrounds[i][1] for i in range(3)]
        new_positions = [
            (bg.centerx + offsets_x[i], bg.centery + offsets_y[i])
            for i, bg in enumerate(backgrounds_rect)
        ]

        # Dessiner les backgrounds
        for i, bg in enumerate(backgrounds_rect):
            screen.blit(backgrounds[i][0], new_positions[i])

    def reset_settings_state(self):
            self.settings_mode = not self.settings_mode
            self.settings_sensi = False
            self.settings_music_vol = False
            self.settings_sfx_vol = False

    def button_affichage(self):
        self.text_level = ""
        clock.tick(85)
        if self.button_shop_created:
            self.creer_button_shop(6)
        if self.button_settings_created:
            self.creer_button_settings(6)
        
        """ Vérifier si une manette est connectée et si elle est utilisée """
        if pygame.joystick.get_count() > 0:
            self.controller_connected = True
        else:
            self.controller_connected = False

        if self.controller_connected:
            pygame.mouse.set_visible(False)  # Masquer le curseur si la manette est branchée
        else:
            pygame.mouse.set_visible(True)   # Afficher le curseur si la manette est débranchée
            self.selected_button_index = 100 * (len(self.button_rects) + 10)
        
        # Get the time for cooldown control
        current_time = pygame.time.get_ticks()

        # Get events from the event queue
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                        self.select_level_clicked = False
                        self.button_game_clicked = False
                        self.activate_button(0)
                        self.activate_button(0)
                        click_sound.play()
                        print("bouton retour")
                if event.key == pygame.K_UP:
                    if self.settings_mode:
                        if self.sensi < 30 and self.settings_sensi:
                            self.sensi += 1
                            self.liste_names_settings[0] = f"VALEUR SENSI {self.sensi}"
                        elif self.music_vol < 100 and self.settings_music_vol:
                            self.music_vol += 5
                            pygame.mixer.music.set_volume(0.3*self.music_vol*0.01)
                            self.liste_names_settings[1] = f"VOL MUSIQUE {self.music_vol}"
                        elif self.sfx_vol < 100 and self.settings_sfx_vol:
                            self.sfx_vol += 5
                            click_sound.set_volume(self.sfx_vol*0.01)
                            coin_sound.set_volume(0.5*self.sfx_vol*0.01)
                            raquette_sound.set_volume(0.8*self.sfx_vol*0.01)
                            dialogue_sound.set_volume(0.7*self.sfx_vol*0.01)
                            game_over_sound.set_volume(self.sfx_vol*0.01)
                            self.liste_names_settings[2] = f"VOL SFX {self.sfx_vol}" 
                if event.key == pygame.K_DOWN:
                    if self.settings_mode:
                        if self.sensi > 1 and self.settings_sensi:
                            self.sensi -= 1
                            self.liste_names_settings[0] = f"VALEUR SENSI {self.sensi}"
                        elif 0 < self.music_vol and self.settings_music_vol:
                            self.music_vol -= 5
                            pygame.mixer.music.set_volume(0.3*self.music_vol*0.01)
                            self.liste_names_settings[1] = f"VOL MUSIQUE {self.music_vol}"
                        elif 0 < self.sfx_vol and self.settings_sfx_vol:
                            self.sfx_vol -= 5
                            click_sound.set_volume(self.sfx_vol*0.01)
                            coin_sound.set_volume(0.5*self.sfx_vol*0.01)
                            raquette_sound.set_volume(0.8*self.sfx_vol*0.01)
                            dialogue_sound.set_volume(0.7*self.sfx_vol*0.01)
                            game_over_sound.set_volume(self.sfx_vol*0.01)
                            self.liste_names_settings[2] = f"VOL SFX {self.sfx_vol}" 
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Manette - boutons
            if self.joystick:
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button == 0:  # Bouton "A"
                        self.activate_button(self.selected_button_index)
                        if menu.select_level_clicked:
                            self.selected_button_index = 1
                        click_sound.play()
                    if event.button == 1:  # Bouton "B"
                        self.select_level_clicked = False
                        self.button_game_clicked = False
                        self.settings_mode = False
                        self.activate_button(0)
                        self.activate_button(0)
                        self.selected_button_index = 0
                        click_sound.play()
                        print("bouton retour")

                # Manette - navigation
                if current_time - self.last_move_time > 200:  # Délai de 200ms pour éviter les répétitions rapides
                    if self.joystick.get_axis(1) > 0.5:  # Vers le bas
                        if self.select_level_clicked:
                            if self.selected_button_index > 15:
                                self.selected_button_index = (self.selected_button_index + 6) % len(self.button_rects)
                            else:
                                self.selected_button_index = (self.selected_button_index + 5) % len(self.button_rects)
                        elif self.button_shop_clicked or self.button_settings_created:
                            if self.settings_mode:
                                if self.sensi > 1 and self.selected_button_index == 3:
                                    self.sensi -= 1
                                    self.liste_names_settings[0] = f"VALEUR SENSI {self.sensi}"
                                elif 0 < self.music_vol and self.selected_button_index == 4:
                                    self.music_vol -= 5
                                    pygame.mixer.music.set_volume(0.3*self.music_vol*0.01)
                                    self.liste_names_settings[1] = f"VOL MUSIQUE {self.music_vol}"
                                elif 0 < self.sfx_vol and self.selected_button_index == 5:
                                    self.sfx_vol -= 5
                                    click_sound.set_volume(self.sfx_vol*0.01)
                                    coin_sound.set_volume(0.5*self.sfx_vol*0.01)
                                    raquette_sound.set_volume(0.8*self.sfx_vol*0.01)
                                    dialogue_sound.set_volume(0.7*self.sfx_vol*0.01)
                                    game_over_sound.set_volume(self.sfx_vol*0.01)
                                    self.liste_names_settings[2] = f"VOL SFX {self.sfx_vol}" 
                            else:
                                if self.selected_button_index < 3:
                                    self.selected_button_index = (self.selected_button_index + 1) % 3
                                else:
                                    if self.selected_button_index > 6:
                                        self.selected_button_index = (self.selected_button_index + 2) % (len(self.button_rects) - 3)
                                    else:
                                        self.selected_button_index = (self.selected_button_index + 2) % len(self.button_rects)
                        else:
                            self.selected_button_index = (self.selected_button_index + 1) % len(self.button_rects)
                        self.last_move_time = current_time
                    elif self.joystick.get_axis(1) < -0.5:  # Vers le haut
                        if menu.select_level_clicked:
                            if 0 < self.selected_button_index < 6:
                                self.selected_button_index = (self.selected_button_index - 6) % len(self.button_rects)
                            elif self.selected_button_index != 0:
                                self.selected_button_index = (self.selected_button_index - 5) % len(self.button_rects)
                        elif menu.button_shop_clicked or menu.button_settings_created:
                            if self.settings_mode:
                                if self.sensi < 30 and self.selected_button_index == 3:
                                    self.sensi += 1
                                    self.liste_names_settings[0] = f"VALEUR SENSI {self.sensi}"
                                elif self.music_vol < 100 and self.selected_button_index == 4:
                                    self.music_vol += 5
                                    pygame.mixer.music.set_volume(0.3*self.music_vol*0.01)
                                    self.liste_names_settings[1] = f"VOL MUSIQUE {self.music_vol}"
                                elif self.sfx_vol < 100 and self.selected_button_index == 5:
                                    self.sfx_vol += 5
                                    click_sound.set_volume(self.sfx_vol*0.01)
                                    coin_sound.set_volume(0.5*self.sfx_vol*0.01)
                                    raquette_sound.set_volume(0.8*self.sfx_vol*0.01)
                                    dialogue_sound.set_volume(0.7*self.sfx_vol*0.01)
                                    game_over_sound.set_volume(self.sfx_vol*0.01)
                                    self.liste_names_settings[2] = f"VOL SFX {self.sfx_vol}" 
                            else:
                                if self.selected_button_index < 3:
                                    self.selected_button_index = (self.selected_button_index - 1) % 3
                                else:
                                    if self.selected_button_index < 5:
                                        self.selected_button_index = (self.selected_button_index + 4) % (len(self.button_rects))
                                    else:
                                        self.selected_button_index = (self.selected_button_index - 2) % len(self.button_rects)
                        elif not (menu.select_level_clicked and menu.button_shop_clicked):
                            self.selected_button_index = (self.selected_button_index - 1) % len(self.button_rects)
                        self.last_move_time = current_time
                    elif self.joystick.get_axis(0) > 0.5:  # Vers la droite
                        if menu.select_level_clicked:
                            self.selected_button_index = (self.selected_button_index + 1) % len(self.button_rects)
                        elif menu.button_shop_clicked or menu.button_settings_created:
                            if self.settings_mode:
                                pass
                            else:
                                if self.selected_button_index > 2 and self.selected_button_index % 2 == 0:
                                    self.selected_button_index = int(self.selected_button_index // 3) - 1
                                elif self.selected_button_index > 2:
                                    self.selected_button_index = (self.selected_button_index + 1) % len(self.button_rects)
                        self.last_move_time = current_time
                    elif self.joystick.get_axis(0) < -0.5:  # Vers la gauche
                        if menu.select_level_clicked:
                            self.selected_button_index = (self.selected_button_index - 1) % len(self.button_rects)
                        elif menu.button_shop_clicked or menu.button_settings_created:
                            if self.settings_mode:
                                pass
                            else:
                                if self.selected_button_index < 3:
                                    self.selected_button_index = 2*self.selected_button_index + 4
                                elif self.selected_button_index > 2 and (self.selected_button_index + 1) % 2:
                                    self.selected_button_index = (self.selected_button_index - 1) % len(self.button_rects)
                        self.last_move_time = current_time
                

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, button_rect in enumerate(self.button_rects):
                    if button_rect.collidepoint(event.pos):
                        self.activate_button(i)
                click_sound.play()

        # Call the parallax method to draw the background
        self.parallax()

        # Afficher les boutons et la sélection manette
        for i, (button_surface, button_rect, button_text) in enumerate(zip(self.button_surfaces, self.button_rects, self.button_texts)):
            # Si la manette est en mode sélection sur le bouton
            if i == self.selected_button_index:
                if self.settings_mode:
                    pygame.draw.rect(button_surface, (100, 200, 0), (0, 0, self.button_menu_x, self.button_menu_y))
                else:
                    pygame.draw.rect(button_surface, (200, 200, 0), (0, 0, self.button_menu_x, self.button_menu_y))
            elif button_rect.collidepoint(pygame.mouse.get_pos()):
                if self.settings_mode and i == 3 and self.settings_sensi:
                    pygame.draw.rect(button_surface, (100, 200, 0), (0, 0, self.button_menu_x, self.button_menu_y))
                elif self.settings_mode and i == 4 and self.settings_music_vol:
                    pygame.draw.rect(button_surface, (100, 200, 0), (0, 0, self.button_menu_x, self.button_menu_y))
                elif self.settings_mode and i == 5 and self.settings_sfx_vol:
                    pygame.draw.rect(button_surface, (100, 200, 0), (0, 0, self.button_menu_x, self.button_menu_y))
                else:
                    pygame.draw.rect(button_surface, (200, 200, 0), (0, 0, self.button_menu_x, self.button_menu_y))
            else:
                if i not in (jeu.liste_acces) and i > 1 and not (self.button_shop_clicked or self.button_settings_created) and self.button_game_clicked:
                    pygame.draw.rect(button_surface, (55, 55, 55), (0, 0, self.button_menu_x, self.button_menu_y))
                else:
                    if self.settings_mode and i == 3 and self.settings_sensi:
                        pygame.draw.rect(button_surface, (100, 200, 0), (0, 0, self.button_menu_x, self.button_menu_y))
                    elif self.settings_mode and i == 4 and self.settings_music_vol:
                        pygame.draw.rect(button_surface, (100, 200, 0), (0, 0, self.button_menu_x, self.button_menu_y))
                    elif self.settings_mode and i == 5 and self.settings_sfx_vol:
                        pygame.draw.rect(button_surface, (100, 200, 0), (0, 0, self.button_menu_x, self.button_menu_y))
                    else:
                        pygame.draw.rect(button_surface, (255, 255, 255), (0, 0, self.button_menu_x, self.button_menu_y))
                pygame.draw.rect(button_surface, (0, 0, 0), (0, self.button_menu_y - 5*delta_h, self.button_menu_x, 5*delta_h), 0)

            button_text_rect = button_text.get_rect(center=(button_surface.get_width() / 2, button_surface.get_height() / 2))
            button_surface.blit(button_text, button_text_rect)
            screen.blit(button_surface, (button_rect.x, button_rect.y))

        pygame.draw.rect(screen, BLANC, (10 * delta_w, 10 * delta_h, (500 + 27 * (len(str(money.money)) - 1)) * delta_w, 47 * delta_h))
        screen.blit(money.texte_noir, (20 * delta_w, 20 * delta_h))
        pygame.display.update()
        
    def activate_button(self, button_index):
        print(f"Button {button_index + 1} clicked")
        self.button_game_clicked = True
        self.button_created = False
        if button_index == 0 and not self.select_level_clicked:  # Sélection du niveau
            self.select_level_clicked = True
            menu.button_shop_clicked = False
            menu.button_shop_created = False
            menu.button_settings_created = False
            self.reset_settings_state()
            self.settings_mode = False
            print(f"select_level_clicked: {self.select_level_clicked}")
            print("menu niveaux ouvert")
        elif button_index == 1 and not self.select_level_clicked:  # Shop
            money.shop = True
            menu.button_game_clicked = False
            menu.creer_button_shop(6)
            menu.button_shop_clicked = True
            menu.button_settings_created = False
            self.reset_settings_state()
            self.settings_mode = False
            print(money.money)
        elif button_index == 2 and not self.select_level_clicked: #settings
            self.reset_settings_state()
            self.settings_mode = False
            money.shop = False
            menu.button_shop_created  = False
            menu.button_game_clicked = False
            menu.creer_button_settings(6)
            menu.button_shop_clicked = False
            menu.button_settings_created = True
        elif menu.button_shop_clicked:  # Actions dans le shop
            self.reset_settings_state()
            self.settings_mode = False
            if button_index == 3:  # profit + 1
                if money.money - int((money.plus_profit + 2) * 5 ** 1.1) >= 0:
                    money.enlever(int((money.plus_profit + 2) * 5 ** 1.1))
                    money.depense += int((money.plus_profit + 2) * 5 ** 1.1)
                    money.plus_profit += 1
            elif button_index == 4:  # + 1 dmg
                if money.money - int((money.degats_owned + 2) * 10 ** 1.1) >= 0:
                    money.enlever(int((money.degats_owned + 2) * 10 ** 1.1))
                    money.depense += int((money.degats_owned + 2) * 10 ** 1.1)
                    money.degats_owned += 1
            elif button_index == 5:
                if money.boom == 256 and money.money >= 256:
                    money.enlever(256)
                    money.depense += 256
                    money.boom = "OUI"
                    money.dgt_boom = False
            elif button_index == 6:
                if money.drone == 512 and money.money >= 512:
                    money.enlever(512)
                    money.depense += 512
                    money.drone = "OUI"
                    money.dgt_drone = False
            elif button_index == 7:
                money.money += money.depense    # rembourser
                money.depense = 0   # pour eviter dupli
                money.ajouter(0)    # pour afficher salaire
                money.plus_profit = 1   # valeur base
                money.degats_owned = 0
                money.boom = 256
                money.drone = 512
                money.dgt_drone = True
                money.dgt_boom = True
            elif button_index == 8:
                money.money += money.depense    # rembourser
                money.depense = 0   # pour eviter dupli
                money.ajouter(0)    # pour afficher salaire
                money.plus_profit = 1   # valeur base
                money.degats_owned = 0
                money.boom = 256
                money.drone = 512
                money.dgt_drone = True
                money.dgt_boom = True
            # Ajouter les autres actions du shop ici
        elif menu.button_settings_created: # Actions dans les settings
            if button_index == 3: # set sensi
                self.reset_settings_state()
                self.settings_sensi = True
            elif button_index == 4: # vol music
                self.reset_settings_state()
                self.settings_music_vol = True
            elif button_index == 5: # vol sfx
                self.reset_settings_state()
                self.settings_sfx_vol = True
            elif button_index == 6:
                save_game(money, jeu, menu)
            elif button_index == 7:
                pass
            elif button_index == 8:
                pass
            
        elif button_index == 0:  # Bouton retour
            self.reset_values_after_loose()
            self.select_level_clicked = False
            self.button_game_clicked = False
            self.button_shop_clicked = False
            self.button_created = True
            self.reset_settings_state()
            self.settings_mode = False
            print("bouton retour")
        else:  # Sélection d'un niveau
            self.reset_settings_state()
            self.settings_mode = False
            self.select_level_clicked = False
            menu.button_shop_created = False
            self.level_selected = button_index
            print(f"level_selected: {self.level_selected}")
            self.text_level = big_font.render(f"NIVEAU {self.level_selected}: {self.liste_titres[self.level_selected - 1]}", True, BLANC)
            self.text_rect_in_level = self.text_level.get_rect(x = 20 * delta_w , y = (47 + 20) * delta_h)
    

balle = Balle()
menu = Menu()
jeu = Jeu()
raquette = Raquette()
dialogue = Dialogue()

# Fonction pour sauvegarder les données dans un fichier JSON
def save_game(money, jeu, menu, filename='game_data.json'):
    data = {
        'money': money.to_dict(),
        'jeu': jeu.to_dict(),
        'menu': menu.to_dict()
    }
    with open(filename, 'w') as f:
        json.dump(data, f)

# Fonction pour charger toutes les données depuis un fichier JSON
def load_game(money, jeu, menu, filename='game_data.json'):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            money.from_dict(data.get('money', {}))
            jeu.from_dict(data.get('jeu', {}))
            menu.from_dict(data.get('menu', {}))
    else:
        print("Pas de fichier de sauvegarde trouvé, utilisation des valeurs par défaut.")

load_game(money, jeu, menu)

print("jeu lancé")
while True:
    if menu.controller_connected:
        pygame.mouse.set_pos((10, 10))
    if menu.select_level_clicked:
        if not menu.button_created:
            menu.creer_button_level(20)
            print(f"button_created: {menu.button_created}")
            menu.button_created = True
        else:
            menu.button_affichage()
    elif menu.button_game_clicked and not (menu.button_shop_clicked or menu.button_settings_created):
        if not jeu.perdu and menu.level_selected in jeu.liste_acces: # boucle dans niveau
            jeu.gestion_evenements()
            jeu.mise_a_jour()
            jeu.affichage()
            menu.button_game_clicked = True
        elif jeu.endscreen:
            jeu.mise_a_jour()
            jeu.affichage()
        elif jeu.win:
            jeu.win_func()
        elif jeu.perdu: #ecran game over
            jeu.game_over()
        else:
            menu.reset_values_after_loose()
            menu.button_created = True
    else:
        if menu.button_created:
            menu.creer_button_menu(3)
            print(f"button_created: {menu.button_created}")
            menu.button_created = False
        menu.button_affichage()
    pygame.display.update()
    clock.tick(85)
print("sortie de boucle anormale")