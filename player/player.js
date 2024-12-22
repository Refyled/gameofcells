// player.js
const axios = require('axios');

// URL de base de votre serveur Node
// (changez si votre serveur est ailleurs)
const BASE_URL = 'http://localhost:3000';

// Nom de joueur qu'on aimerait prendre (p1, p2, etc.)
let desiredPlayerName = 'p1';

// On va stocker le vrai nom qu'on obtient après connexion
let myPlayerName = null;

// Stocke le dernier tour pour éviter de rejouer 2 fois sur le même tour
let lastTurnPlayed = null;

// Petite boucle asynchrone pour orchestrer le tout
async function main() {
  try {
    // 1) Vérifier la liste des joueurs connectés
    const playersResp = await axios.get(`${BASE_URL}/players`);
    const connectedPlayers = playersResp.data.connectedPlayers || [];

    // 2) Si desiredPlayerName est déjà pris, on incrémente (p2, p3, p4, etc.)
    //    On fait une petite boucle pour trouver un nom dispo
    let suffix = 1;
    let base = desiredPlayerName.replace(/\d+$/, ''); // ex: "p"
    let nameCandidate = desiredPlayerName;
    while (connectedPlayers.includes(nameCandidate)) {
      suffix++;
      nameCandidate = base + suffix; 
      // ex. "p" + 2 => "p2"
    }

    // 3) On tente de se connecter avec ce nameCandidate
    console.log(`Tentative de connexion avec le nom "${nameCandidate}"...`);
    await axios.post(`${BASE_URL}/join`, { name: nameCandidate });
    myPlayerName = nameCandidate;

    console.log(`Connecté en tant que "${myPlayerName}".`);

    // On lance une boucle infinie qui :
    //  - Récupère /state
    //  - Si le tour a changé, on envoie nos moves
    setInterval(checkAndPlay, 2000); // toutes les 2 secondes

  } catch (error) {
    console.error("Erreur dans main:", error.message);
  }
}

// Cette fonction est appelée toutes les 2s
// pour regarder l'état et potentiellement jouer si le tour a changé.
async function checkAndPlay() {
  try {
    // 1) Récupérer /state
    const stateResp = await axios.get(`${BASE_URL}/state`);
    const { turn, grid, grid_size, timeBetweenMoves, players } = stateResp.data;

    // 2) Si le tour n'a pas changé depuis la dernière fois, on ne joue pas
    if (turn === lastTurnPlayed) {
      return; 
    }

    // 3) On récupère nos cellules (celles qui ont player == myPlayerName)
    const myCells = grid.filter(cell => cell.player === myPlayerName);
    if (myCells.length === 0) {
      // On n'a pas de cellule sur la grille => rien à jouer
      console.log(`Tour ${turn} : pas de cellule pour ${myPlayerName}`);
      lastTurnPlayed = turn;
      return;
    }

    // 4) Construire un move "aléatoire" en séparant au maximum chaque cell
    //    C'est-à-dire si une cell a weight=4, on envoie 4 "morceaux" de weight=1.
    //    Chacun va dans une direction au hasard (y compris "stay").
    //    => on calcule pour chaque cell la répartition.
    const movesForThisTurn = [];

    // Pour chaque cellule
    myCells.forEach(cell => {
      const { weight } = cell;
      // On va générer weight "sous-mouvements", chacun de weight=1
      // On compte combien vont up/down/left/right/stay
      // Ensuite on fera la somme pour un "move_up", etc.

      // 5 directions possibles : up/down/left/right/stay
      let countUp = 0;
      let countDown = 0;
      let countLeft = 0;
      let countRight = 0;
      let countStay = 0;

      for (let i = 0; i < weight; i++) {
        // random pick in [0..4]
        const dir = Math.floor(Math.random() * 5);
        switch(dir) {
          case 0: countUp++; break;
          case 1: countDown++; break;
          case 2: countLeft++; break;
          case 3: countRight++; break;
          case 4: countStay++; break;
        }
      }

      movesForThisTurn.push({
        x: cell.x,
        y: cell.y,
        player: myPlayerName,
        move_up: countUp,
        move_down: countDown,
        move_left: countLeft,
        move_right: countRight,
        move_stay: co
