from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, emit
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
rooms = {}

def create_board(rows, cols, mines):
    board = [[{'mine': False, 'revealed': False, 'flagged': False, 'adjacent': 0} for _ in range(cols)] for _ in range(rows)]
    mine_positions = random.sample([(r, c) for r in range(rows) for c in range(cols)], mines)
    for r, c in mine_positions:
        board[r][c]['mine'] = True
    for r in range(rows):
        for c in range(cols):
            if board[r][c]['mine']:
                continue
            adj_mines = sum(1 for dr in [-1,0,1] for dc in [-1,0,1]
                            if 0 <= r+dr < rows and 0 <= c+dc < cols and board[r+dr][c+dc]['mine'])
            board[r][c]['adjacent'] = adj_mines
    return board

def reveal_cell(board, r, c):
    stack = [(r, c)]
    while stack:
        r, c = stack.pop()
        if not (0 <= r < len(board) and 0 <= c < len(board[0])):
            continue
        cell = board[r][c]
        if cell['revealed'] or cell['flagged']:
            continue
        cell['revealed'] = True
        if cell['adjacent'] == 0 and not cell['mine']:
            for dr in [-1,0,1]:
                for dc in [-1,0,1]:
                    nr, nc = r+dr, c+dc
                    if dr == 0 and dc == 0:
                        continue
                    if 0 <= nr < len(board) and 0 <= nc < len(board[0]):
                        neighbor = board[nr][nc]
                        if not neighbor['revealed'] and not neighbor['flagged']:
                            stack.append((nr, nc))

def get_opponent_boards(room, exclude_sid):
    opponent_boards = {}
    for sid_, board in rooms[room]['players'].items():
        if sid_ != exclude_sid:
            opponent_board = []
            for row in board:
                opponent_row = []
                for cell in row:
                    if cell['flagged']:
                        opponent_row.append('🏴')
                    elif cell['revealed']:
                        if cell['mine']:
                            opponent_row.append('💣')
                        else:
                            opponent_row.append(str(cell['adjacent']) if cell['adjacent'] > 0 else '')
                    else:
                        opponent_row.append('■')
                opponent_board.append(opponent_row)
            opponent_boards[sid_] = opponent_board
    return opponent_boards

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        room = request.form['room']
        return redirect(url_for('game', room=room))
    return render_template('index.html')

@app.route('/game/<room>')
def game(room):
    return render_template('game.html', room=room)

@socketio.on('join')
def on_join(data):
    room = data['room']
    sid = request.sid
    join_room(room)

    if room not in rooms:
        rooms[room] = {'players': {}}

    if sid not in rooms[room]['players']:
        board = create_board(10, 10, 10)
        rooms[room]['players'][sid] = board

    # Отправляем собственное поле игроку
    emit('load_board', rooms[room]['players'][sid], to=sid)

    # Обновляем поля оппонентов для игрока
    opponent_boards = get_opponent_boards(room, exclude_sid=sid)
    emit('update_opponents', opponent_boards, to=sid)

@socketio.on('reveal')
def on_reveal(data):
    room = data['room']
    sid = request.sid
    r, c = data['cell']
    board = rooms[room]['players'][sid]

    if not (0 <= r < len(board) and 0 <= c < len(board[0])):
        return

    cell = board[r][c]
    if cell['revealed'] or cell['flagged']:
        return

    if cell['mine']:
        cell['revealed'] = True
        emit('game_over', room=sid)
        # Можно реализовать логику окончания игры, если нужно
    else:
        reveal_cell(board, r, c)

    # Отправляем обновленное поле игроку
    emit('load_board', board, to=sid)

    # Обновляем поля оппонентов для всех игроков в комнате
    for player_sid in rooms[room]['players']:
        if player_sid != sid:
            opponent_boards = get_opponent_boards(room, exclude_sid=player_sid)
            emit('update_opponents', opponent_boards, to=player_sid)

@socketio.on('flag')
def on_flag(data):
    room = data['room']
    sid = request.sid
    r, c = data['cell']
    board = rooms[room]['players'][sid]

    if not (0 <= r < len(board) and 0 <= c < len(board[0])):
        return

    cell = board[r][c]
    if cell['revealed']:
        return

    cell['flagged'] = not cell['flagged']

    # Отправляем обновленное поле игроку
    emit('load_board', board, to=sid)

    # Обновляем поля оппонентов для всех игроков в комнате
    for player_sid in rooms[room]['players']:
        if player_sid != sid:
            opponent_boards = get_opponent_boards(room, exclude_sid=player_sid)
            emit('update_opponents', opponent_boards, to=player_sid)

@socketio.on('disconnect')
def on_disconnect():
    sid = request.sid
    # Удаляем игрока из всех комнат
    for room in list(rooms.keys()):
        if sid in rooms[room]['players']:
            del rooms[room]['players'][sid]
            # Обновляем поля оппонентов для всех оставшихся игроков
            for player_sid in rooms[room]['players']:
                opponent_boards = get_opponent_boards(room, exclude_sid=player_sid)
                emit('update_opponents', opponent_boards, to=player_sid)
            # Если в комнате нет игроков, удаляем комнату
            if not rooms[room]['players']:
                del rooms[room]

if __name__ == '__main__':
    socketio.run(app, debug=True)
