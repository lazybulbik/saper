from flask import Flask, redirect, url_for, request, render_template, make_response
from loader import app, socketio


import api


@app.route('/')
def index():
    ip = request.remote_addr

    response = make_response(render_template('index.html'))
    
    # Установка заголовков, предотвращающих кеширование
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


@app.route('/game/<room>')
def game(room):
    return render_template('game.html', room=room)



if __name__ == '__main__':
    socketio.run(app, debug=True, host='95.142.38.61', port=5001)