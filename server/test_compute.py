# test_compute.py

from compute import compute_game_turn

def main():
    # Paramètres du jeu
    grid_size = 6
    numberOfVit = 2  # On veut 2 vitamines au total

    # Grille initiale : trois ou quatre cellules pour tester les merges
    original_grid = [
        {'x': 2, 'y': 2, 'weight': 4, 'player': 'p1'},       # Cellule de p1 poids 4
        {'x': 2, 'y': 3, 'weight': 2, 'player': 'p1'},       # Cellule de p1 poids 2 (même joueur)
        {'x': 3, 'y': 2, 'weight': 3, 'player': 'p2'},       # Cellule de p2 poids 3
        {'x': 5, 'y': 5, 'weight': 1, 'player': 'vitamin'}   # Une vitamine
    ]

    # Moves tentés :
    #  1) La cellule p1 en (2,2) veut se diviser : 2 qui montent, 2 qui restent
    #  2) La cellule p1 en (2,3) veut descendre ses 2 points (mais c'est potentiellement un move illégal s'il sort de la grille, à voir)
    #  3) La cellule p2 en (3,2) veut bouger à gauche (1) et en bas (2)
    #  4) On ne donne pas de move pour la vitamine (5,5), donc elle restera en place
    cells_moves = [
        {
            'x': 2,
            'y': 2,
            'player': 'p1',
            'move_up': 2,
            'move_down': 0,
            'move_left': 0,
            'move_right': 0,
            'move_stay': 2
        },
        {
            'x': 2,
            'y': 3,
            'player': 'p1',
            'move_up': 0,
            'move_down': 2,
            'move_left': 0,
            'move_right': 0,
            'move_stay': 0
        },
        {
            'x': 3,
            'y': 2,
            'player': 'p2',
            'move_up': 0,
            'move_down': 2,
            'move_left': 1,
            'move_right': 0,
            'move_stay': 0
        }
    ]

    # On appelle la fonction de compute.py
    move_animation, new_grid = compute_game_turn(
        grid_size,
        numberOfVit,
        original_grid,
        cells_moves
    )

    # Affichage des résultats
    print("\n=== Move Animation ===")
    for anim in move_animation:
        print(anim)

    print("\n=== Nouvelle Grille ===")
    for cell in new_grid:
        print(cell)

if __name__ == "__main__":
    main()