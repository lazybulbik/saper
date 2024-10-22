socketio = io();
const room = document.getElementById('room').value;

const rows = 15
const cols = 15
const bombs_precent = 0.2

socketio.emit('join', {'room': room})

var genEmptyField = () => Array.from({ length: 15 }, () => Array(15).fill({ opened: false, value: -1, flag: false }));

function fillTable(el, tableData, isMine = true) {
    el.innerHTML = ''
    console.log('Fill table')
    for (let y = 0; y < tableData.length; y++) {
        let row = document.createElement('tr')
        for (let x = 0; x < tableData[y].length; x++) {
            console.log(tableData[y][x])
            let cell = document.createElement('td')
            cell.classList.add('cell')
            cell.classList.add('closed')
            cell.setAttribute('data-x', x)
            cell.setAttribute('data-y', y)

            if (isMine) {
                cell.addEventListener('click', onCellClick)
                cell.addEventListener('contextmenu', onCellRightClick)
            }

            if (tableData[y][x]['flag']) {
                cell.classList.add('flag')
                cell.innerHTML = '🚩'
            }             

            if (!tableData[y][x]['opened']) {
                row.appendChild(cell)
                continue
            }
            
            if (tableData[y][x]['value'] == -1) {
                cell.classList.add('bomb')
                cell.innerHTML = '💣'
                alert('Игра окночена. Бум! Бам! Взрывы!')
            } else {
                if (tableData[y][x]['value'] == 0) {
                    cell.innerHTML = ' '
                } else {
                    cell.innerHTML = tableData[y][x]['value']
                }
            }

            cell.classList.add('opened')            

            row.appendChild(cell)
        }
        el.appendChild(row)
    }
}

function onCellClick(event) {
    controlBtns = document.querySelectorAll('.action-btn')

    if (controlBtns[0].classList.contains('selected')) {
        onCellRightClick(event)
        return
    }

    const x = event.target.getAttribute('data-x')
    const y = event.target.getAttribute('data-y')
    socketio.emit('click', {'x': x, 'y': y, 'room': room, 'rows': rows, 'cols': cols, 'bombs_precent': bombs_precent, 'action': 'open'})
}

function onCellRightClick(event) {    
    event.preventDefault()
    const x = event.target.getAttribute('data-x')
    const y = event.target.getAttribute('data-y')
    socketio.emit('click', {'x': x, 'y': y, 'room': room, 'rows': rows, 'cols': cols, 'bombs_precent': bombs_precent, 'action': 'flag'})
}

document.getElementById('flag-btn').addEventListener('click', (event) => {
    event.target.classList.toggle('selected')
    document.getElementById('open-btn').classList.remove('selected')
})

document.getElementById('open-btn').addEventListener('click', (event) => {
    event.target.classList.toggle('selected')
    document.getElementById('flag-btn').classList.remove('selected')
})


socketio.on('update-field', (tableData) => {
    fillTable(document.getElementById('field'), tableData)

    // console.log(tableData)
})

socketio.on('update-enemies-fields', (tableData) => {
    tableList = document.getElementById('enemies-fields')
    tableList.innerHTML = ''

    console.log(tableData)

    for (let i = 0; i < tableData.length; i++) {
        let table = document.createElement('table')
        
        fillTable(table, tableData[i], false)
        tableList.appendChild(table)
    };
})


document.addEventListener('DOMContentLoaded', () => {
    console.log('Game started')
    const field = Array.from({ length: 15 }, () => Array(15).fill({ opened: false, value: -1, flag: false }));
    // console.log(field)
    fillTable(document.getElementById('field'), field)
})