(function () {
    const CELL_COLOR0 = '<div class="cell-color0"></div></div>';
    const CELL_COLOR1 = '<div class="cell-color1"><div id="circle" class="nopawn"></div>';
    const CELL_COLOR1_PLAYER1_REGULAR_PAWN = '<div class="cell-color1"><div id="circle" class="player1-pawn-regular"></div>';
    const CELL_COLOR1_PLAYER2_REGULAR_PAWN = '<div class="cell-color1"><div id="circle" class="player2-pawn-regular"></div>';
    const BOARD_SIZE = 8;

    let gridContainer = document.querySelector('#container');
    for (let i = 0; i < BOARD_SIZE; i++) {
        for (let j = 0; j < BOARD_SIZE; j++) {
            if ((i + j) % 2 == 0) {
                gridContainer.insertAdjacentHTML('beforeend', CELL_COLOR0);
            } else {
                if (i < BOARD_SIZE / 2 - 1) {
                    gridContainer.insertAdjacentHTML('beforeend', CELL_COLOR1_PLAYER1_REGULAR_PAWN);
                }
                else if (i >= BOARD_SIZE / 2 + 1) {
                    gridContainer.insertAdjacentHTML('beforeend', CELL_COLOR1_PLAYER2_REGULAR_PAWN);
                }
                else {
                    gridContainer.insertAdjacentHTML('beforeend', CELL_COLOR1);
                }
            }
        }
    }
})();


const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/checkers/'
    + 'default'
    + '/'
);

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const cells = document.querySelectorAll("#container div.cell-color1 div")
    const cellsCount = Math.min(data.message.length, cells.length);
    const pawnTypesArr = ["nopawn", "player1-pawn-regular", "player1-pawn-king", "player2-pawn-regular", "player2-pawn-king"]
    for (let i = 0; i < cellsCount; i++) {
        let pawn_type = data.message[i]
        cells.item(i).className = pawnTypesArr[pawn_type]
    }
};

chatSocket.onclose = function (e) {
    console.error('Chat socket closed unexpectedly');
};
