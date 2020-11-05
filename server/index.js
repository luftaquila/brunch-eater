const fs = require('fs');
const io = require('socket.io')(3151);
const dirTree = require("directory-tree");
const spawn = require("child_process").spawn;

io.sockets.on('connection', function (socket) {
  let python;
  socket.on('execute', function (query) {
    python = spawn('python3' /*query.data.command*/, [query.data.file, '-k', query.data.keyword, ...query.data.option.split(' ')]);
    python.stdout.on('data', (data) => { io.to(socket.id).emit('progress', data.toString()); });
    python.on('close', (code) => { io.to(socket.id).emit('SIGTERM', code); });
  });
  socket.on('SIGKILL', function() {
    try {
      python.kill();
    }
    catch(e) { }
  });
  socket.on('load', function() {
    const tree = dirTree('../outputs/');
    io.to(socket.id).emit('filelist', tree);
  });
  socket.on('delete', (data) => {
    fs.unlink('../outputs/' + data, (err) => { });
    const tree = dirTree('../outputs/');
    io.to(socket.id).emit('filelist', tree);
  });
});