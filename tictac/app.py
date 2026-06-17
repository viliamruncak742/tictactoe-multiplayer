import os
import uuid

from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")

socketio = SocketIO(app, cors_allowed_origins="*")

# --- Herný stav (v pamäti, žiadna databáza) ---------------------------------
rooms = {}        # room_id -> {"players": {sid: symbol}, "board": [...], "turn": "X", "winner": None}
sid_to_room = {}  # sid -> room_id
waiting_room_id = None

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # riadky
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # stĺpce
    (0, 4, 8), (2, 4, 6),             # diagonály
]


def check_winner(board):
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if "" not in board:
        return "draw"
    return None


def room_state(game):
    return {"board": game["board"], "turn": game["turn"], "winner": game.get("winner")}


@app.route("/")
def index():
    return render_template("index.html")


@socketio.on("connect")
def on_connect():
    global waiting_room_id
    sid = request.sid

    if waiting_room_id is None:
        # Nový hráč si vytvorí miestnosť a čaká na súpera
        room_id = uuid.uuid4().hex[:6]
        rooms[room_id] = {
            "players": {sid: "X"},
            "board": [""] * 9,
            "turn": "X",
            "winner": None,
        }
        sid_to_room[sid] = room_id
        join_room(room_id)
        waiting_room_id = room_id
        emit("waiting", {"message": "Čakám na súpera..."})
    else:
        room_id = waiting_room_id
        game = rooms[room_id]
        game["players"][sid] = "O"
        sid_to_room[sid] = room_id
        join_room(room_id)
        waiting_room_id = None

        # Každému hráčovi pošleme jeho symbol osobne
        for player_sid, symbol in game["players"].items():
            emit("start", {"symbol": symbol, **room_state(game)}, room=player_sid)


@socketio.on("disconnect")
def on_disconnect():
    global waiting_room_id
    sid = request.sid
    room_id = sid_to_room.pop(sid, None)
    if room_id is None:
        return

    if room_id == waiting_room_id:
        waiting_room_id = None

    game = rooms.pop(room_id, None)
    if game:
        for other_sid in game["players"]:
            if other_sid != sid:
                emit("opponent_left", {"message": "Súper opustil hru."}, room=other_sid)
                sid_to_room.pop(other_sid, None)


@socketio.on("move")
def on_move(data):
    sid = request.sid
    room_id = sid_to_room.get(sid)
    if not room_id or room_id not in rooms:
        return

    game = rooms[room_id]
    if len(game["players"]) < 2:
        return  # súper ešte nepripojený

    symbol = game["players"].get(sid)
    index = data.get("index")

    if symbol is None or index is None:
        return
    if game["winner"]:
        return
    if game["turn"] != symbol:
        return
    if not (0 <= index < 9) or game["board"][index] != "":
        return

    game["board"][index] = symbol
    game["winner"] = check_winner(game["board"])
    if not game["winner"]:
        game["turn"] = "O" if symbol == "X" else "X"

    emit("update", room_state(game), room=room_id)


@socketio.on("restart")
def on_restart():
    sid = request.sid
    room_id = sid_to_room.get(sid)
    if not room_id or room_id not in rooms:
        return

    game = rooms[room_id]
    if len(game["players"]) < 2:
        return

    game["board"] = [""] * 9
    game["turn"] = "X"
    game["winner"] = None
    emit("update", room_state(game), room=room_id)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port)
