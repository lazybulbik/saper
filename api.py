from flask import render_template, request, make_response, redirect
from flask_socketio import SocketIO, emit

from loader import app, ROOMS, socketio

import utils


@socketio.on('connect')
def connect():
    socketio.emit('update-rooms', {'names': list(ROOMS.keys())})


@socketio.on('create-room')
def create_room(data):
    room_name = data['roomName']
    print(room_name)

    if room_name not in ROOMS:
        ROOMS[room_name] = {}
        emit('update-rooms', {'names': list(ROOMS.keys())}, broadcast=True)



@socketio.on('join')
def join(data):
    room_name = data['room']
    print(room_name)

    if room_name not in ROOMS:
        ROOMS[room_name] = {}
        emit('update-rooms', {'names': list(ROOMS.keys())}, broadcast=True)
        
    ROOMS[room_name][request.sid] = {'field': None}

    fields = utils.get_fields_for_room(room_name)
    for user in fields:
        socketio.emit('update-enemies-fields', fields[user], to=user)

@socketio.on('click')
def create_field(data):
    x = int(data['x'])
    y = int(data['y'])
    room_name = data['room']

    cols = int(data['cols'])
    rows = int(data['rows'])
    bombs_precent = float(data['bombs_precent'])

    action = data['action']

    print(x, y, room_name, cols, rows, bombs_precent, action)

    if ROOMS[room_name][request.sid]['field'] is None:
        print('Generate field')
        ROOMS[room_name][request.sid]['field'] = utils.generate_field(cols, rows, bombs_precent, safe_zone=(x, y))
        field = utils.open_cell(ROOMS[room_name][request.sid]['field'], x, y, action=action)
        ROOMS[room_name][request.sid]['field'] = field

    else:
        print('Open cell')
        field = utils.open_cell(ROOMS[room_name][request.sid]['field'], x, y, action=action)
        ROOMS[room_name][request.sid]['field'] = field


    emit('update-field', ROOMS[room_name][request.sid]['field'])

    fields = utils.get_fields_for_room(room_name)
    for user in fields:
        socketio.emit('update-enemies-fields', fields[user], to=user)    

@socketio.on('empty')
def empty_field(data):
    room_name = data['room']
    ROOMS[room_name][request.sid]['field'] = None
    
    fields = utils.get_fields_for_room(room_name)
    for user in fields:
        socketio.emit('update-enemies-fields', fields[user], to=user)

@socketio.on('disconnect')
def disconnect():
    for room in ROOMS:
        if request.sid in ROOMS[room]:
            del ROOMS[room][request.sid]

            if len(ROOMS[room]) == 0:
                del ROOMS[room]

            emit('update-rooms', {'names': list(ROOMS.keys())}, broadcast=True)

            fields = utils.get_fields_for_room(room=room)
            for user in fields:
                socketio.emit('update-enemies-fields', fields[user], to=user)

    print('Client disconnected')
