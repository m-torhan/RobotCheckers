var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
})

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/checkers/'
    + 'default'
    + '/'
);

chatSocket.onopen = function (e) {
    addCommunicate("Połączenie z robotem pomyślne.");
}

chatSocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    const message_type = data.type;
    switch (message_type) {
        case 'game_status':
            updateWhosTurn(data.message.game_status);
            gameStatusHandler(data.message.game_status);
            break;
        case 'move':
            document.getElementsByClassName("turn")[0].children[1].innerHTML = data.message.id+1;
            movePawn(data.message.move_steps, data.message.new_board_status , data.message.taken_pawns);
            break;
        case 'toast':
            addToast(data.message.msg);
            break;
        default:
            console.log(`Unsupported message type: ${expr}`);
    }
};

chatSocket.onclose = function (e) {
    addCommunicate("Połączenie z robotem zostało niespodziewanie zakończone!");
    addToast("Komunikacja zerwana");
};



function gameStatusHandler(status) {
    
}

function initBoard(){
    const table = document.getElementById("gameboard");      
    let i = 8;
    while (--i>=0) {
      const row = document.createElement("tr");
      let j=8;
      while(--j>=0) {
        row.appendChild(document.createElement("td"));        
      }
      table.appendChild(row);
    }
  };

  // takes flatten string representing board and insert pawn on the right places
  function placePawns(board){          
    for (let index = 0; index < board.length; index++) {
      const element = board[index];
      if("1234".includes(element)){
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
        document.getElementById("gameboard").getElementsByTagName("tr")[parseInt(index/4)].children[parseInt(((index)%4)*2+((index/4+1)%2))].appendChild(pawn);
      }
    }
  }

  function updateWhosTurn(whosTurn){
    if(whosTurn == "ROBOTS_MOVE_STARTED"){
      document.getElementsByClassName("whos-move")[0].children[1].innerHTML = "Robot"
    }
    else if(whosTurn == "PLAYERS_MOVE_STARTED"){
      document.getElementsByClassName("whos-move")[0].children[1].innerHTML = "Gracz"
    }
  }

  function addCommunicate(text){
    const p = document.createElement("p");
    p.innerHTML =  "> "+ text;
    var scrollArea = document.getElementsByClassName("card")[0];
    scrollArea.children[0].appendChild(p)
    scrollArea.scrollTop = scrollArea.scrollHeight;
  }

  function sleep(ms) {return new Promise(resolve => setTimeout(resolve, ms));}

  async function movePawn(move_list, output_board, taken_pawns){
    var x = 0, y = 0;

    // make moves
    for (let i = 0; i < move_list.length - 1; i++){
      x += move_list[i+1]["x"] - move_list[i]["x"];
      y += move_list[i+1]["y"] - move_list[i]["y"];
      document.getElementsByTagName("td")[move_list[0]["y"]*8+move_list[0]["x"]].children[0].classList.add("animate-move");
      document.getElementsByTagName("td")[move_list[0]["y"]*8+move_list[0]["x"]].children[0].style.transform = 
      "translate(" + (x)*125 + "%," + (y)*125 + "%)";

      await sleep(1000);
    }
 
    // fade away taken pawns
    for (let index = 0; index < taken_pawns.length; index++) {
      const element = taken_pawns[index];
      document.getElementsByTagName("td")[element["y"]*8+element["x"]].children[0].classList.add("fader");
    }
    await sleep(1000);
    
    // clear board
    var el = document.getElementsByTagName('td');
    for (let index = 0; index < el.length; index++) {
      const element = el[index];
      while ( element.firstChild ) element.removeChild( element.firstChild );
    }
    
    // place new board status
    placePawns(output_board);
    await sleep(1000);
  }

  async function addToast(communicate){
    document.getElementsByClassName("toast-body")[0].innerText = communicate;
    var toastLiveExample = document.getElementById("liveToast");
    var toast = new bootstrap.Toast(toastLiveExample);
    toast.show();      
  }