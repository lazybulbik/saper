sio = io()

function shake(el){
    el.classList.add('shake')
    setTimeout(() => {
        el.classList.remove('shake')
    }, 500)
}

document.getElementById('create-room').addEventListener('click', () => {
    let roomName = document.getElementById('room-name').value
    if (roomName) {
        sio.emit('create-room', {'roomName': roomName})
        document.getElementById('room-name').value = ''
    } else {
        shake(document.getElementById('room-name'))
    }
})

sio.on('update-rooms', (data) => {
    roomsList = document.getElementById('rooms')
    roomsList.innerHTML = ''

    data['names'].forEach(room => {
        room = `<div class="room" onclick="window.location.href = '/game/${room}'"><h4>${room}</h4></div>`
        roomsList.innerHTML += room
    })
})