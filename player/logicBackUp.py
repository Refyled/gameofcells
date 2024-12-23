# logic.py

import random

def get_valid_directions(x, y, grid_size):
    """
    Retourne les directions valides pour une cellule donnée en fonction de sa position et de la taille de la grille.
    """
    directions = []
    if y > 0:
        directions.append('move_up')
    if y < grid_size - 1:
        directions.append('move_down')
    if x > 0:
        directions.append('move_left')
    if x < grid_size - 1:
        directions.append('move_right')
    directions.append('move_stay')  # Toujours possible

    return directions

def build_moves(grid, my_player_name, grid_size):
    """
    Construit une liste de moves pour ce tour.
    Si une cellule a un poids > 1, il y a une chance de diviser le poids entre deux directions aléatoires valides.
    """
    moves_for_this_turn = []

    # Filtrer les cellules du joueur
    my_cells = [c for c in grid if c.get('player') == my_player_name]
    if not my_cells:
        return []

    for cell in my_cells:
        x = cell.get('x')
        y = cell.get('y')
        weight = cell.get('weight', 1)

        # Obtenir les directions valides pour cette cellule
        valid_directions = get_valid_directions(x, y, grid_size)

        if not valid_directions:
            # Aucune direction valide, rester sur place
            move = {
                "x": x,
                "y": y,
                "player": my_player_name,
                "move_up": 0,
                "move_down": 0,
                "move_left": 0,
                "move_right": 0,
                "move_stay": weight
            }
            moves_for_this_turn.append(move)
            continue

        move = {
            "x": x,
            "y": y,
            "player": my_player_name,
            "move_up": 0,
            "move_down": 0,
            "move_left": 0,
            "move_right": 0,
            "move_stay": 0
        }

        if weight <= 1:
            # Déplacer tout le poids dans une direction aléatoire
            direction = random.choice(valid_directions)
            move[direction] = weight
        else:
            # Décider aléatoirement de diviser le poids
            should_divide = random.random() < 0.5  # 50% de chance de diviser
            if should_divide and len(valid_directions) >= 2:
                # Choisir deux directions distinctes
                direction1, direction2 = random.sample(valid_directions, 2)
                # Diviser le poids de manière aléatoire
                split_point = random.randint(1, weight - 1)
                move[direction1] = split_point
                move[direction2] = weight - split_point
            else:
                # Ne pas diviser, déplacer tout le poids dans une direction
                direction = random.choice(valid_directions)
                move[direction] = weight

        moves_for_this_turn.append(move)

    return moves_for_this_turn
