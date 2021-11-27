const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});

const webSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/checkers/'
    + 'default'
    + '/'
);

webSocket.onopen = function (e) {
    addEventToRegister("Połączenie z robotem pomyślne.");
}

webSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const message_type = data.type;
    switch (message_type) {
        case 'game_status':
            updateWhosTurn(data.message.game_status);
            gameStatusHandler(data.message.game_status);
            addToast(data.message.content)
            break;
        case 'move':
            document.getElementsByClassName("turn")[0].children[1].innerHTML = data.message.id + 1;
            movePawn(data.message.move_steps, data.message.new_board_status, data.message.taken_pawns);

            break;
        case 'toast':
            addToast(data.message.msg);
            break;
        default:
            console.log(`Unsupported message type: ${expr}`);
    }
};

webSocket.onclose = function (e) {
    addEventToRegister("Połączenie z robotem zostało niespodziewanie zakończone!");
    addToast("Komunikacja zerwana");
};


function gameStatusHandler(status) {

}

function initBoard() {
    const table = document.getElementById("gameboard");
    let i = 8;
    while (--i >= 0) {
        const row = document.createElement("tr");
        let j = 8;
        while (--j >= 0) {
            row.appendChild(document.createElement("td"));
        }
        table.appendChild(row);
    }
    sessionStorage.setItem('whoMoves', 'Gracz');
    sessionStorage.setItem('toggleStartStopRobot', '0')
};

// takes flatten string representing board and insert pawn on the right places
function placePawns(board) {
    for (let index = 0; index < board.length; index++) {
        const element = board[index];
        if ("1234".includes(element)) {
            const pawn = document.createElement("div");
            switch (parseInt(element)) {
                case 1:
                    pawn.classList.add("pawn", "white");
                    break;
                case 2:
                    pawn.classList.add("pawn", "blue");
                    break;
                case 3:
                    pawn.classList.add("pawn", "black");
                    break;
                case 4:
                    pawn.classList.add("pawn", "red");
                    break;
            }
            document.getElementById("gameboard").getElementsByTagName("tr")[parseInt(index / 4)].children[parseInt(((index) % 4) * 2 + ((index / 4 + 1) % 2))].appendChild(pawn);
        }
    }
}

function updateWhosTurn(whosTurn) {
    if (whosTurn === "ROBOTS_MOVE_STARTED") {
        document.getElementsByClassName("whos-move")[0].children[1].innerHTML = "Robot";
    } else if (whosTurn === "PLAYERS_MOVE_STARTED") {
        document.getElementsByClassName("whos-move")[0].children[1].innerHTML = "Gracz";
    }
    sessionStorage.setItem('whoMoves', sessionStorage.getItem('whoMoves') === 'Gracz' ? 'Robot' : 'Gracz');
}

function addEventToRegister(text) {
    const p = document.createElement("p");
    p.innerHTML = "> " + text;
    const scrollArea = document.getElementsByClassName("card")[0];
    scrollArea.children[0].appendChild(p)
    scrollArea.scrollTop = scrollArea.scrollHeight;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function movePawn(move_list, output_board, taken_pawns) {
    let x = 0, y = 0;

    // make moves
    for (let i = 0; i < move_list.length - 1; i++) {
        x += move_list[i + 1]["x"] - move_list[i]["x"];
        y += move_list[i + 1]["y"] - move_list[i]["y"];

        document.getElementsByTagName("td")[move_list[0]["y"] * 8 + move_list[0]["x"]].children[0].classList.add("animate-move");
        document.getElementsByTagName("td")[move_list[0]["y"] * 8 + move_list[0]["x"]].children[0].style.transform =
            "translate(" + (x) * 125 + "%," + (y) * 125 + "%)";

        addEventToRegister(`${sessionStorage.getItem('whoMoves')} wykonał ruch z pola (${move_list[i]["x"]},${move_list[i]["y"]}) do (${move_list[i + 1]["x"]},${move_list[i + 1]["y"]})`);

        await sleep(1000);
    }

    // promote pawns
    if (move_list.length !== 0 && (move_list[move_list.length - 1]['y'] === 0 || move_list[move_list.length - 1]['y'] === 7)) {
        const pawn = document.getElementsByTagName("td")[move_list[0]["y"] * 8 + move_list[0]["x"]].children[0];
        if (pawn.classList.contains('white')) {
            pawn.classList.remove('white');
            pawn.classList.add('promotion')
            pawn.classList.add('blue');
        }
        if (pawn.classList.contains('black')) {
            pawn.classList.remove('black');
            pawn.classList.add('promotion');
            pawn.classList.add('red');
        }
    }

    // fade away taken pawns
    for (let index = 0; index < taken_pawns.length; index++) {
        const element = taken_pawns[index];
        document.getElementsByTagName("td")[element["y"] * 8 + element["x"]].children[0].classList.add("fader");
    }
    await sleep(1000);

    // clear board
    const el = document.getElementsByTagName('td');
    for (let index = 0; index < el.length; index++) {
        const element = el[index];
        while (element.firstChild) element.removeChild(element.firstChild);
    }

    // place new board status
    placePawns(output_board);
    await sleep(1000);
}

async function addToast(content) {
    if (content !== '') {
        document.getElementsByClassName("toast-body")[0].innerText = content;
        const toastLiveExample = document.getElementById("liveToast");
        const toast = new bootstrap.Toast(toastLiveExample);
        toast.show();
    }
}

function toggleStartStopRobot() {
    const toggleStatus = sessionStorage.getItem('toggleStartStopRobot');
    if (toggleStatus === '0') {
        sendUserAction('stop_robot');
        document.getElementById('startStopRobotButton').innerText = 'Wznów ruch robota';
    } else {
        sendUserAction('resume_robot');
        document.getElementById('startStopRobotButton').innerText = 'Zatrzymaj robota';
    }
    sessionStorage.setItem('toggleStartStopRobot', toggleStatus === '0' ? '1' : '0')
}

let UserActions = {
    'end_game': 'Żądanie zakończenia rozgrywki wysłane do robota.',
    'stop_robot': 'Żądanie wstrzymania ruchu robota zostało wysłane.',
    'resume_robot': 'Żądanie wznowienia ruchu ramienia zostało wysłane.'
}

function sendUserAction(type) {
    webSocket.send(JSON.stringify({'type': 'user_action', 'message': {'content': type}}));
    addToast(UserActions[type]);
}
