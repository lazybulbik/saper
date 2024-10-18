from flask import render_template, request, make_response, redirect
from flask_socketio import SocketIO, emit

from loader import app, ROOMS

import utils


@app.route('/api/get_rooms')
def get_rooms():
    result = []

    for room in ROOMS:
        if len(ROOMS[room]) != 2:
            result.append(room)

    return {'rooms': result}


@app.route('/api/create_room', methods=['POST'])
def create_room():
    room_key = utils.generate_key(4)

    ROOMS[room_key] = []

    return {'key': room_key}


@app.route('/api/get_field')
def get_field():
    return {'field': utils.generate_field(30, 30, 0.15)}