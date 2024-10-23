socketio = io();
const ROOM = document.getElementById('room').value;
socketio.emit('join', {'room': ROOM})

const BOMBS_PERCENT = 0.2

let rows = 15
let cols = 15

const FLAG_BTN = document.getElementById('flag-btn')
const OPEN_BTN = document.getElementById('open-btn')

const RESET_BTN = document.getElementById('reset-btn')

var genEmptyField = () => Array.from({ length: rows }, () => Array(cols).fill({ opened: false, value: -1, flag: false }));

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

function onCellRightClick(event) {
    event.preventDefault()
    onCellClick(event, 'flag')
}

function onCellClick(event, action) {
    if (action == undefined)
    {
        action = FLAG_BTN.classList.contains('selected') ? 'flag' : 'open'
    }

    const x = event.target.getAttribute('data-x')
    const y = event.target.getAttribute('data-y')
    socketio.emit('click', {'x': x, 'y': y, 'room': ROOM, 'rows': rows, 'cols': cols, 'bombs_precent': BOMBS_PERCENT, 'action': action})
}

FLAG_BTN.addEventListener('click', (event) => {
    FLAG_BTN.classList.toggle('selected')
    OPEN_BTN.classList.remove('selected')
})

OPEN_BTN.addEventListener('click', (event) => {
    OPEN_BTN.classList.toggle('selected')
    FLAG_BTN.classList.remove('selected')
})

RESET_BTN.addEventListener('click', (e) => {
    console.log("Empty the field.");

    socketio.emit('empty', {'room': ROOM})

    const field = genEmptyField();
    fillTable(document.getElementById('field'), field)
})

socketio.on('update-field', (tableData) => {
    fillTable(document.getElementById('field'), tableData)
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
    const field = genEmptyField();
    // console.log(field)
    fillTable(document.getElementById('field'), field)
})