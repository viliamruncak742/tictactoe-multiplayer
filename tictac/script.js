const socket = io();

const statusEl = document.getElementById("status");
const boardEl = document.getElementById("board");
const cells = Array.from(document.querySelectorAll(".cell"));
const restartBtn = document.getElementById("restart-btn");
const winLineEl = document.getElementById("win-line");
const youBadge = document.getElementById("you-badge");
const youSymbolEl = document.getElementById("you-symbol");

let mySymbol = null;
let gameActive = false;

const WIN_LINES = [
  { cells: [0, 1, 2], cls: "win-line--row0" },
  { cells: [3, 4, 5], cls: "win-line--row1" },
  { cells: [6, 7, 8], cls: "win-line--row2" },
  { cells: [0, 3, 6], cls: "win-line--col0" },
  { cells: [1, 4, 7], cls: "win-line--col1" },
  { cells: [2, 5, 8], cls: "win-line--col2" },
  { cells: [0, 4, 8], cls: "win-line--diag-main" },
  { cells: [2, 4, 6], cls: "win-line--diag-anti" },
];

function setStatus(text, mine = false) {
  statusEl.textContent = text;
  statusEl.classList.toggle("status--mine", mine);
}

function renderBoard(board) {
  cells.forEach((cell, i) => {
    cell.textContent = board[i] || "";
    cell.classList.remove("is-x", "is-o");
    if (board[i] === "X") cell.classList.add("is-x");
    if (board[i] === "O") cell.classList.add("is-o");
  });
}

function updateCellAvailability(board, turn, winner) {
  const myTurn = !winner && turn === mySymbol;
  gameActive = myTurn;
  cells.forEach((cell, i) => {
    cell.disabled = !myTurn || Boolean(board[i]);
  });
}

function showWinLine(board, winner) {
  winLineEl.hidden = true;
  winLineEl.className = "win-line";
  if (!winner || winner === "draw") return;

  const line = WIN_LINES.find(
    (l) => board[l.cells[0]] === winner && board[l.cells[1]] === winner && board[l.cells[2]] === winner
  );
  if (!line) return;

  winLineEl.classList.add(line.cls);
  winLineEl.hidden = false;
}

function describeState(turn, winner) {
  if (winner === "draw") return "Remíza! 🤝";
  if (winner) {
    return winner === mySymbol ? "Vyhral si! 🎉" : "Prehral si. 😅";
  }
  return turn === mySymbol ? "Si na ťahu" : "Čaká sa na súpera...";
}

socket.on("waiting", (data) => {
  setStatus(data.message || "Čakám na súpera...");
  cells.forEach((cell) => (cell.disabled = true));
  restartBtn.hidden = true;
  youBadge.hidden = true;
});

socket.on("start", (data) => {
  mySymbol = data.symbol;
  youSymbolEl.textContent = mySymbol;
  youBadge.hidden = false;
  renderBoard(data.board);
  updateCellAvailability(data.board, data.turn, data.winner);
  showWinLine(data.board, data.winner);
  setStatus(describeState(data.turn, data.winner), data.turn === mySymbol);
  restartBtn.hidden = true;
});

socket.on("update", (data) => {
  renderBoard(data.board);
  updateCellAvailability(data.board, data.turn, data.winner);
  showWinLine(data.board, data.winner);
  setStatus(describeState(data.turn, data.winner), data.turn === mySymbol && !data.winner);
  restartBtn.hidden = !data.winner;
});

socket.on("opponent_left", (data) => {
  setStatus(data.message || "Súper opustil hru.");
  cells.forEach((cell) => (cell.disabled = true));
  restartBtn.hidden = true;
});

cells.forEach((cell) => {
  cell.addEventListener("click", () => {
    if (!gameActive || cell.disabled) return;
    const index = Number(cell.dataset.index);
    socket.emit("move", { index });
  });
});

restartBtn.addEventListener("click", () => {
  socket.emit("restart");
});
