const ws = require('ws');

const client = new ws('ws://localhost:3000');

client.on('open', () => {
  let list = Array(32).fill(1);
  let message = JSON.stringify(list)
  client.send(message);
});