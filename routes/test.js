var express = require('express');
var router = express.Router();

var io = require('socket.io')(3001);

json_data = JSON.stringify(true);    //query_data는 json타입 이므로 stringify 해줌
const {PythonShell} = require('python-shell');
const options = {
  mode: 'text',
  pythonPath: "C:/Users/S170710A/Anaconda3/envs/racing/python.exe",
  pythonOptions: ['-u'],
  scriptPath: 'cheonghwa/',    // 실행할 py 파일 path. 현재 nodejs파일과 같은 경로에 있어 생략
  args: null
};
var pyshell = new PythonShell('main.py',options);

var clients = [];
var require_num = 0;
var complete_num = 1;


pyshell.on('message', function (message) {
  // received a message sent from the Python script (a simple "print" statement)
  console.log('from python : '+ message);

  if(message=='error'){
    pyshell.end(function (err,code,signal) {
      if (err) throw err;
      console.log('The exit code was: ' + code);
      console.log('The exit signal was: ' + signal);
      console.log('finished');
      console.log('finished');
    });
  }else if(message == '1') {
    io.sockets.emit('ddd');
    io.sockets.emit('ppp','현재'+((require_num)-complete_num++)+'명 대기중입니다.');
    io.sockets.emit('ooo','누적'+(require_num)+'명 사용했습니다.');
  }

});

io.sockets.on('connection', function (socket) {
  //console.log(socket.id);
  //clients.push(socket.id);
  //socket.join(socket.id);
  console.log("enter user : " + socket.id);
  //console.log("now user : "+clients);
  //socket.on('call', function (data) {});
  socket.on('disconnect', function () {
    console.log("exit user : " + socket.id);
    //clients.pop(socket.id);
  });
});

var multer = require('multer');
var fs = require('fs');
var filename;

var storage = multer.diskStorage({
  destination: function (req,file,cb) {
    cb(null,'./public/upload/');
  },
  filename: function (req,file,cb) {
    var ip = req.headers['x-forwarded-for'] ||
        req.connection.remoteAddress ||
        req.socket.remoteAddress ||
        req.connection.socket.remoteAddress;
    var realip = ip.split(":")[3].replace(/\./gi,"-");
    var year = new Date().getFullYear();
    var month = new Date().getMonth()+1;
    var day = new Date().getDate();
    var hour = new Date().getHours();
    var minute = new Date().getMinutes();
    var sec = new Date().getSeconds();
    filename = realip+'_'+year+'-'+month+'-'+day+'_'+hour+'-'+minute+'-'+sec;
    //console.log(filename);
    cb(null,filename+'.'+file.originalname.split('.')[1]);
  }
})
var upload = multer({
  storage: storage,
  limits: { fileSize: 20000000  },
  fileFilter: function (req, file, callback)
  {
    if (file.mimetype.indexOf('image') === -1) {
      // 현재 테스트를 이미지로만 할꺼기에 이미지로 세팅.
      callback(null, false);
    }
    else if(file.mimetype.indexOf('gif') != -1)
    {
      callback(null, false);
    } else {
      callback(null, true);
      require_num++;
    }
  }
});

router.use(express.static('./public/upload/'));

router.get('/', function(req, res, next) {
  res.render('test');
});



router.post('/receive',upload.single('userfile'),function (req,res,next) {

  //console.log("require_num : "+require_num);
  //console.log("complete_num : "+complete_num);
  if(req.file != undefined) {
    console.log(req.file.originalname);
    pyshell.send([filename ,req.file.originalname.split('.')[1]]);
    //require_num++;
    var template = `
    <!DOCTYPE html>
    <html>
      <head>
      <script type="text/javascript" src="https://code.jquery.com/jquery-1.12.4.min.js"></script>
      <script type="text/javascript" src="https://cdn.socket.io/socket.io-1.3.5.js"></script>
      <script language='javascript'>

        function noEvent() {
            if (event.keyCode == 116) {
                event.keyCode= 2;
                return false;
            }
            else if(event.ctrlKey && (event.keyCode==78 || event.keyCode == 82)){
                return false;
            }
        }
        document.onkeydown = noEvent;
        history.pushState(null, null, location.href);
        window.onpopstate = function () {
            history.go(1);
        };
        </script>
        <title>Python Test</title>
        <link rel=\'stylesheet\' href=\'/stylesheets/style.css\' />
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1.0">
      </head>
      <body oncontextmenu="return false">
      <h1><a href="http://cvlab308.iptime.org:3000/"/>  Python Test </a></h1>
       <img src= ${filename+'.'+req.file.originalname.split('.')[1]} width="192" height="108">Before
       <img id="test" src="loading.gif" width="192" height="108">After
       <button onclick="goReplace('/test/')" >다른사진 올리기</button>
       <p id="answer1">${'누적'+(require_num)+'명 사용했습니다.'}</p>
       <p id="answer2">${'현재'+((require_num)-complete_num)+'명 대기중입니다.'}</p>
        <script>
          function goReplace(str) { location.replace(str); }
          
          var socket = io.connect('http://cvlab308.iptime.org:3001');
          $('#test') 
            .error(function() { 
                $("#test").attr("src","loading.gif");
            }) 
            .attr("src","${filename+'_result.'+req.file.originalname.split('.')[1]}"); 
          
          socket.on('ddd',function() {
              $("#test").attr("src","${filename+'_result.'+req.file.originalname.split('.')[1]}");
          });
          
          socket.on('ppp',function(data) {
              $("#answer2").text(data);
          });
          socket.on('ooo',function(data) {
              $("#answer1").text(data);
          });
        </script>
       </body>
    </html>
  `
   res.send(template);
  }
  else{
    res.send(`<script>alert("파일을 선택해주세요!");location.replace(/test/);</script>`);
  }

});

module.exports = router;
