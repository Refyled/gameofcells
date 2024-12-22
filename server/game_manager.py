from compute import generate_initial_grid, compute_game_turn

class GameManager:
    def __init__(self, players, grid_size, start_weight, number_of_vitamins):
        """
        Initialise une partie avec une grille de départ
        """
        self.grid_size = grid_size
        self.number_of_vitamins = number_of_vitamins
        self.players = players
        self.start_weight = start_weight
        # On génère la grille initiale
        self.current_grid = generate_initial_grid(
            players, grid_size, start_weight, number_of_vitamins
        )

    def reset(self):
        """
        Ré-initialise la grille (optionnel si vous voulez relancer une partie).
        """
        self.current_grid = generate_initial_grid(
            self.players, 
            self.grid_size, 
            self.start_weight, 
            self.number_of_vitamins
        )

    def apply_moves(self, cells_moves):
        """
        Applique un tour de jeu et met à jour la grille courante
        :param cells_moves: liste de moves (dict)
        :return: (move_animation, new_grid)
        """
        move_animation, new_grid = compute_game_turn(
            self.grid_size,
            self.number_of_vitamins,
            self.current_grid,
            cells_moves
        )
        self.current_grid = new_grid
        return move_animation, new_grid

    def get_state(self):
        """
        Retourne la grille courante.
        """
        return self.current_grid