fetch('/api/get_rooms', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json'
    }
}).then((response) => {
    return response.json();
}).then((data) => {
    console.log(data);
    gameList = document.getElementById('game-list');
    data['rooms'].forEach(element => {
        let game = document.createElement('div');
        game.classList.add('game');
        game.innerHTML = element;
        game.addEventListener('click', () => {
            window.location.href = `/game/${element}`
        })
        gameList.append(game);
    });
})


document.getElementById('create-game').addEventListener('click', () => {
    fetch('/api/create_room', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    }).then((response) => {
        return response.json();
    }).then((data) => {
        window.location.href = `/game/${data['key']}`
    })
})