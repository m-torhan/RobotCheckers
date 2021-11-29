function sendSettings() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/settings", false);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send(JSON.stringify({
        'difficulty': document.getElementById("difficulty").value,
        'start_mode': document.querySelector('input[name="start_mode"]:checked').value
    }));
    if(xhr.status == 200){
        window.location = xhr.responseURL
    }
}

difficulty.addEventListener('input', setRangeLabel, false);
function setRangeLabel(){
    let labels = [
        'Losowo',
        'MonteCarlo 1',
        'MonteCarlo 2',
        'MonteCarlo 3',
        'MinMax 1',
        'MinMax 2',
        'MinMax 3',
        'AlphaBeta 1',
        'AlphaBeta 2',
        'AlphaBeta 3'
    ];
    var difficulty_value = document.getElementById("difficulty").value; 
    document.getElementById("difficulty-label").innerText = labels[difficulty_value-1];
}