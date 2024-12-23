// player_nodivision.js
const axios = require('axios');

const BASE_URL = 'http://localhost:3000';  // Adresse où tourne votre serveur Node
let desiredPlayerName = 'p1';             // Nom de joueur souhaité
let myPlayerName = null;                  // Nom final après connexion
let lastTurnPlayed = null;                // Pour éviter de rejouer sur le même tour

async function main() {
  try {
    // 1) Récupérer la liste des joueurs connectés
    const playersResp = await axios.get(`${BASE_URL}/players`);
    const connectedPlayers = playersResp.data.connectedPlayers || [];

    // 2) Trouver un nom libre (p1, p2, etc.)
    let suffix = 1;
    let base = desiredPlayerName.replace(/\d+$/, ''); // ex: "p" 
    let nameCandidate = desiredPlayerName;
    while (connectedPlayers.includes(nameCandidate)) {
      suffix++;
      nameCandidate = base + suffix;
    }

    // 3) Se connecter via POST /join
    console.log(`Tentative de connexion avec le nom "${nameCandidate}"...`);
    await axios.post(`${BASE_URL}/join`, { name: nameCandidate });
    myPlayerName = nameCandidate;

    console.log(`Connecté en tant que "${myPlayerName}".`);

    // 4) Vérifier régulièrement l'état et jouer si nécessaire
    setInterval(checkAndPlay, 2000);
  } catch (error) {
    console.error("Erreur dans main:", error.message);
  }
}

async function checkAndPlay() {
  try {
    // 1) Récupérer /state
    const stateResp = await axios.get(`${BASE_URL}/state`);
    const { turn, grid, grid_size, timeBetweenMoves, players } = stateResp.data;

    // 2) Si on a déjà joué pour ce tour, ne pas rejouer
    if (turn === lastTurnPlayed) {
      return;
    }

    // 3) Repérer mes cellules
    const myCells = grid.filter(cell => cell.player === myPlayerName);
    if (myCells.length === 0) {
      console.log(`Tour ${turn}: pas de cellule pour ${myPlayerName}`);
      lastTurnPlayed = turn;
      return;
    }

    // 4) Construire les moves sans division du poids
    //    => tout le poids va dans UNE direction aléatoire
    const movesForThisTurn = myCells.map(cell => {
      // On choisit une direction (0..4) => up/down/left/right/stay
     // const dir = Math.floor(Math.random() * 5);  // 0..4
      const w = cell.weight;
      const dir = 1
      let countUp = 0;
      let countDown = 0;
      let countLeft = 0;
      let countRight = 0;
      let countStay = 0;

      switch (dir) {
        case 0: countUp = w;    break;
        case 1: countDown = w;  break;
        case 2: countLeft = w;  break;
        case 3: countRight = w; break;
        default: countStay = w; break;
      }

      return {
        x: cell.x,
        y: cell.y,
        player: myPlayerName,
        move_up: countUp,
        move_down: countDown,
        move_left: countLeft,
        move_right: countRight,
        move_stay: countStay
      };
    });

    // 5) Afficher dans la console ce qu'on envoie
    console.log(`Tour ${turn}: envoi des moves suivants:`);
    console.log(JSON.stringify(movesForThisTurn, null, 2));

    // 6) Envoyer POST /moves
    const body = {
      player: myPlayerName,
      turn,
      moves: movesForThisTurn
    };

    await axios.post(`${BASE_URL}/moves`, body);
    console.log(`=> Moves envoyés avec succès pour le tour ${turn}\n`);

    // On enregistre qu'on a joué ce tour
    lastTurnPlayed = turn;
  } catch (error) {
    console.error("Erreur dans checkAndPlay:", error.message);
  }
}

// Démarrer le script
main();