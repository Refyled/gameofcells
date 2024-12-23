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


   
