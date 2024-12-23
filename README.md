# Game of Cells

**Game of Cells** is a computer-based strategy game played on a grid. Players control cells with integer weights that interact dynamically. Cells can merge, eat lighter cells and vitamins, or divide and move strategically to gain an advantage. The game progresses with players' moves being processed by deterministic update rules.

Unlike classical cellular automata like Conway's Game of Life, the **Game of Cells** allows players to define stochastic policies for their cells, creating a hybrid of strategic freedom and deterministic progression.

---

## Architecture

The game consists of two main components:

### 1. Node.js Server
The **Node.js** server handles communication with clients using **Express** and **Socket.IO**. It serves as the primary interface and orchestrates game logic requests with the Python backend.

### 2. Python Backend
The Python backend is responsible for processing game logic, including move validation, grid updates, and determining the outcomes of cell interactions.

---

## File Overview

### Core Backend
- **`game_manager.py`**: Manages game states, applying moves and updating the grid dynamically.
- **`compute.py`**: Handles core game logic such as merging cells, resolving conflicts, and placing vitamins.
- **`server.py`**: Python FastAPI server managing game initialization and move submissions.

### Frontend
- **`server.js`**: Node.js server handling client connections, game state updates, and WebSocket events.
- **`front.html`**: Main interface for visualizing the game grid and animations.
- **`settings.html`**: Page for configuring game parameters (e.g., grid size, vitamins).

### Miscellaneous
- **`package.json`**: Node.js project dependencies.
- **`.gitignore`**: Specifies files and directories to exclude from version control.


---

## **API Endpoints and Events Summary**

---
For more details, check api.md

#### **`server.py`**

##### **HTTP Endpoints**

1. **`GET /state`**
   - **Purpose**: Retrieves the current state of the game, including grid configuration, turn information, and player details.

2. **`POST /moves`**
   - **Purpose**: Receives a list of moves for the current turn, processes them, and updates the game state accordingly.

3. **`POST /init`**
   - **Purpose**: Reinitializes the game with new parameters such as grid size, number of vitamins, starting weights, and the list of players.

##### **Socket.IO Events**

1. **`stateUpdate`**
   - **Purpose**: Broadcasts the current game state to all connected clients after each new turn is computed.

2. **`turnAnimation`**
   - **Purpose**: Sends animation details for a specific turn, including movement data and outcomes for cells, to all connected clients.

3. **`join`**
   - **Purpose**: Registers a player to the current game session when a client connects and provides the player's name.

4. **`disconnect`**
   - **Purpose**: Handles a player's disconnection and optionally updates the game state or player list.

---

#### **`server.js`**

##### **HTTP Endpoints**

1. **`GET /`**
   - **Purpose**: Serves the main game interface (`front.html`).

2. **`GET /settings`**
   - **Purpose**: Serves the settings page (`settings.html`) for configuring game parameters.

3. **`GET /players`**
   - **Purpose**: Retrieves the list of currently connected players.

4. **`POST /join`**
   - **Purpose**: Registers a new player to the game.

5. **`POST /begin`**
   - **Purpose**: Starts a new game with custom parameters such as grid size, number of vitamins, starting weight, and time between moves.

6. **`POST /moves`**
   - **Purpose**: Submits a player's moves for the current turn.

##### **Socket.IO Events**

1. **`connection`**
   - **Purpose**: Triggered when a client connects to the server, logs the connection, and initializes communication with the player.

2. **`join`**
   - **Purpose**: Registers a player in the game session via WebSocket.

3. **`disconnect`**
   - **Purpose**: Triggered when a client disconnects from the server and optionally updates the connected players list.

4. **`stateUpdate`**
   - **Purpose**: Sends the current game state, including grid, turn number, grid size, and connected players, to all connected clients.

5. **`turnAnimation`**
   - **Purpose**: Sends animation details for the current turn to all connected clients.

---

   
