const express = require('express');
const ws = require('ws');

const app = express();
app.use("/static/", express.static(__dirname + '/static/'));
app.get("/", (req, res) => {
    res.sendFile(__dirname + "/index.html");
});
// Set up a headless websocket server that prints any
// events that come in.
const wsServer = new ws.Server({ noServer: true });
wsServer.on('connection', socket => {
    socket.on('message', message => {
        console.log(message);

        for (let client of wsServer.clients.values()) {
            if (client !== ws && client.readyState === socket.OPEN) {
                client.send(JSON.stringify(JSON.parse(message)));
            }
        }
    });

    // socket.send(JSON.stringify(Array(32).fill(1)));
});

// `server` is a vanilla Node.js HTTP server, so use
// the same ws upgrade process described here:
// https://www.npmjs.com/package/ws#multiple-servers-sharing-a-single-https-server
const server = app.listen(3000);
server.on('upgrade', (request, socket, head) => {
    wsServer.handleUpgrade(request, socket, head, socket => {
        wsServer.emit('connection', socket, request);
    });
});