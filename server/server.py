# server.py

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from game_manager import GameManager


# ----------------------------------------
# 1) Initialisation du serveur
# ----------------------------------------
app = FastAPI(
    title="GameLogicAPI",
    description="API Python pour gérer la logique du jeu de cellules/vitamines",
    version="1.0.0"
)

class InitParams(BaseModel):
    grid_size: int
    number_of_vitamins: int
    players: List[str]
    start_weight: int

# On initialise un GameManager global (pour 1 partie unique).

players = ["p1", "p2"]          # Joueurs
grid_size = 10
start_weight = 6
number_of_vitamins = 5

game_manager = GameManager(players, grid_size, start_weight, number_of_vitamins)

# ----------------------------------------
# 2) Définition du modèle de données pour recevoir les moves
#    (via Pydantic)
# ----------------------------------------
class Move(BaseModel):
    x: int
    y: int
    player: str
    move_up: int
    move_down: int
    move_left: int
    move_right: int
    move_stay: int

# ----------------------------------------
# 3) Endpoints
# ----------------------------------------

@app.get("/state")
def get_state():
    """
    Récupère l'état courant de la grille (liste de cells/vitamines).
    """
    return game_manager.get_state()

@app.post("/moves")
def post_moves(moves: List[Move]):
    """
    Reçoit un tableau de moves pour ce tour, applique compute_game_turn,
    et renvoie un JSON contenant move_animation + new_grid.
    """
    # Convertit chaque Move Pydantic en dict standard
    moves_list = [m.dict() for m in moves]
    move_animation, new_grid = game_manager.apply_moves(moves_list)
    return {
        "move_animation": move_animation,
        "new_grid": new_grid
    }

@app.post("/init")
def init_game(params: InitParams):
    """
    Ré-initialise la partie avec les nouveaux paramètres reçus
    """
    global game_manager
    # Recrée un nouveau GameManager
    game_manager = GameManager(
        players=params.players,
        grid_size=params.grid_size,
        start_weight=params.start_weight,
        number_of_vitamins=params.number_of_vitamins
    )
    return {
        "message": "Game re-initialized",
        "grid": game_manager.get_state()
    }