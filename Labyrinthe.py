import curses
import random
import time
from collections import deque

# Initialiser curses
stdscr = curses.initscr() # retourne le terminal
curses.noecho() #  Empêche d’afficher automatiquement les touches pressées
curses.cbreak() # Permet de capturer les touches immédiatement sans attendre “Entrée”

# Vérifie si un chemin existe entre l'entrée et la sortie
def labyrinthe_a_solution(labyrinthe, entree, sortie):
    file = deque([entree])  # File (optimisée pour recherche en profondeur)
    visited = set()  # Garde les positions visitées
    visited.add(entree)
    while file:
        x, y = file.popleft()
        if (x, y) == sortie:  # Si on atteint la sortie
            return True
        # Ajouter les voisins accessibles
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Haut, Bas, Gauche, Droite
            nx, ny = x + dx, y + dy
            if 0 <= nx < len(labyrinthe) and 0 <= ny < len(labyrinthe[0]) and (nx, ny) not in visited: 
                if labyrinthe[nx][ny] in {0, 2}:  # Chemin ou sortie
                    file.append((nx, ny))
                    visited.add((nx, ny))
    return False

# Génération d'un labyrinthe avec une solution garantie
def creer_labyrinthe(taille, proportion_chemins=0.7):
    while True:
        labyrinthe = [[1] * taille for _ in range(taille)]  # Labyrinthe rempli de murs
        nb_cases_libres = int(taille * taille * proportion_chemins)
        chemins_positions = random.sample([(i, j) for i in range(taille) for j in range(taille)], nb_cases_libres)

        for x, y in chemins_positions:
            labyrinthe[x][y] = 0  # Définir les chemins libres

        coins = [(0, 0), (0, taille - 1), (taille - 1, 0), (taille - 1, taille - 1)]
        entree = random.choice(coins)
        coins.remove(entree)
        sortie = random.choice(coins)

        labyrinthe[entree[0]][entree[1]] = 3  # Marquer l'entrée
        labyrinthe[sortie[0]][sortie[1]] = 2  # Marquer la sortie

        # Vérifier si le labyrinthe a une solution
        if labyrinthe_a_solution(labyrinthe, entree, sortie):
            return labyrinthe, entree

# Création d'un personnage
def creer_personnage(start):
    return {"char": "o", "x": start[0], "y": start[1]}

# Placement des items aléatoires
def placer_items(labyrinthe, nb_items):
    items = set()
    while len(items) < nb_items:
        x = random.randint(0, len(labyrinthe) - 1)
        y = random.randint(0, len(labyrinthe[0]) - 1)
        if labyrinthe[x][y] == 0:  # Placer uniquement sur les chemins
            items.add((x, y))
    return items

# Afficher le labyrinthe avec curses
def afficher_labyrinthe(labyrinthe, perso, items, dico, chrono, niveau, score_total):
    stdscr.clear()
    max_y, max_x = curses.LINES, curses.COLS # Hauteur et largeur du terminal

    # Vérifier si le terminal est assez grand
    if len(labyrinthe) >= max_y - 1 or len(labyrinthe[0]) >= max_x:
        stdscr.addstr(0, 0, "Terminal trop petit pour afficher le labyrinthe. Agrandissez la fenêtre.")
        stdscr.refresh()
        time.sleep(2)
        return False

    # Afficher le labyrinthe
    for i, ligne in enumerate(labyrinthe):
        for j, cell in enumerate(ligne):
            char = dico.get(cell, str(cell))
            if (i, j) in items:
                char = "."  # Item
            if (i, j) == (perso["x"], perso["y"]):
                char = perso["char"]
            stdscr.addstr(i, j, char)
    stdscr.addstr(len(labyrinthe), 0, f"Score: {score_total} | Items restants: {len(items)} | Temps restant: {chrono:.1f}s | Niveau: {niveau}")
    stdscr.refresh()
    return True

# Mise à jour du personnage selon les touches
def mettre_a_jour_personnage(touche, perso, labyrinthe, items):
    mouvements = {
        "z": (-1, 0),  # Haut
        "s": (1, 0),   # Bas
        "q": (0, -1),  # Gauche
        "d": (0, 1)    # Droite
    }

    if touche in mouvements:
        dx, dy = mouvements[touche]
        new_x, new_y = perso["x"] + dx, perso["y"] + dy
        if 0 <= new_x < len(labyrinthe) and 0 <= new_y < len(labyrinthe[0]): # S'il est dans le lbrt
            if labyrinthe[new_x][new_y] != 1:  # Pas un mur
                perso["x"], perso["y"] = new_x, new_y
                if (new_x, new_y) in items:
                    items.remove((new_x, new_y))  # Ramasser l'item
                if labyrinthe[new_x][new_y] == 2:  # Si c'est la sortie
                    return True, items
    return False, items

# Boucle principale
def jouer():
    niveau = 1
    taille = 10  # Taille fixe du labyrinthe
    nb_items = 5
    temps_par_niveau = 120  # 2 minutes pour le premier niveau
    score_total = 0

    while True:
        labyrinthe, start = creer_labyrinthe(taille)
        perso = creer_personnage(start)
        items = placer_items(labyrinthe, nb_items)
        dico = {0: " ", 1: "#", 2: "S", 3: "E", "o": "o"}

        debut_chrono = time.time()
        chrono_max = temps_par_niveau

        while True:
            chrono = chrono_max - (time.time() - debut_chrono)
            if chrono <= 0:
                stdscr.clear()
                stdscr.addstr(0, 0, f"Temps écoulé ! Vous avez perdu. Score total : {score_total}.")
                stdscr.addstr(2, 0, "Appuyez sur une touche pour quitter.")
                stdscr.refresh()
                stdscr.nodelay(False) # Attend que l’utilisateur appuie sur une touche avant de continuer
                stdscr.getkey() # Attend que l’utilisateur appuie sur une touche 
                return  # Fin du jeu

            if not afficher_labyrinthe(labyrinthe, perso, items, dico, chrono, niveau, score_total):
                continue  # Ne pas avancer tant que le terminal est trop petit

            stdscr.nodelay(True)
            try:
                touche = stdscr.getkey()
            except:
                touche = None

            if touche == "p":
                stdscr.clear()
                stdscr.addstr(0, 0, f"Vous avez quitté le jeu. Score total : {score_total}.")
                stdscr.refresh()
                stdscr.nodelay(False)
                stdscr.getkey()
                return  # Quitter le jeu
            elif touche:
                termine, items = mettre_a_jour_personnage(touche, perso, labyrinthe, items)
                if termine:
                    score_total += 100 + ( nb_items - len(items) )  # +100 pour finir le niveau + items restants
                    niveau += 1
                    temps_par_niveau -= 15
                    break 

# Exécuter le jeu
try:
    jouer()
finally:
    curses.nocbreak()
    curses.echo()
    curses.endwin() # tous ces paramètres reviennent à leur état initial