# test_compute.py

from compute import generate_initial_grid, compute_game_turn

def print_ascii_grid(cells, grid_size):
    """
    Affiche la grille de taille grid_size x grid_size,
    avec un caractère pour chaque occupant :
      - '.' si la case est vide
      - 'V' si c'est une vitamine
      - un identifiant ex: '1', '2', '3'... s'il s'agit d'un joueur p1, p2, p3, etc.
    (Vous pouvez affiner selon vos besoins.)
    """

    # Prépare une matrice de '.' (cases vides)
    board = [['.' for _ in range(grid_size)] for _ in range(grid_size)]

    # Place chaque occupant
    for cell in cells:
        x = cell['x']
        y = cell['y']
        player = cell['player']

        if player == 'vitamin':
            ch = 'V'
        else:
            # ex: "p1" => '1', "p2" => '2', "p10" => '10' (ou juste '0', à adapter)
            # Pour simplifier, on prend tout sauf le premier caractère 'p'
            # s'il commence par 'p', sinon on met '?'
            if player.startswith('p'):
                ch = player[1:]  # ex: "p1" -> "1"
            else:
                ch = '?'  # dans le doute
        board[y][x] = ch  # On place le caractère

    # On affiche la grille, en partant du haut (y = grid_size-1) vers le bas (y = 0)
    # pour avoir un repère "visuel" plus classique.
    for row_index in reversed(range(grid_size)):
        row = board[row_index]
        print(" ".join(row))
    print()  # Ligne vide à la fin

def main():
    # --- Paramètres ---
    grid_size = 6
    number_of_vitamins = 2
    players = ['p1', 'p2']
    start_weight = 4

    # --- 1) Génération de la grille initiale ---
    original_grid = generate_initial_grid(players, grid_size, start_weight, number_of_vitamins)
    print("=== Grille AVANT le mouvement ===")
    print_ascii_grid(original_grid, grid_size)

    # --- 2) Création d'un tableau de moves (exemple) ---
    # Supposons que la cellule p1 veuille bouger à droite et p2 reste immobile (ou essaie un truc).
    cells_moves = [
        {
            'x': 2,        # On suppose p1 est vers x=2, y=?
            'y': 3,        # A ajuster en fonction de la position réellement générée
            'player': 'p1',
            'move_up': 0,
            'move_down': 0,
            'move_left': 0,
            'move_right': 4,   # tout son poids (4) va à droite
            'move_stay': 0
        },
        {
            'x': 3,
            'y': 2,
            'player': 'p2',
            'move_up': 0,
            'move_down': 0,
            'move_left': 0,
            'move_right': 0,
            'move_stay': 4     # p2 ne bouge pas
        }
    ]

    # NOTE : Dans la pratique, il faut vérifier les coordonnées de p1/p2 dans la grille générée.
    # Ici, on illustre juste un exemple. Vous devrez peut-être ajuster x, y en fonction
    # de la position réelle retournée par generate_initial_grid().

    # --- 3) Appel de la fonction compute_game_turn ---
    move_animation, new_grid = compute_game_turn(
        grid_size,
        number_of_vitamins,
        original_grid,
        cells_moves
    )

    # --- 4) Affichage des résultats ---
    print("=== Move Animation ===")
    for m in move_animation:
        print(m)

    print("\n=== Grille APRES le mouvement ===")
    print_ascii_grid(new_grid, grid_size)

if __name__ == "__main__":
    main()