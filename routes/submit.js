var express = require('express');
var router = express.Router();
var multer = require('multer');
var fs = require('fs');
var storage = multer.diskStorage({
    destination: function (req,file,cb) {
        cb(null,'public/upload/');
    },
    filename: function (req,file,cb) {
        cb(null,file.originalname);
    }
})
var upload = multer({
    storage: storage,
    limits: { fileSize: 20000000  },
    fileFilter: function (req, file, callback)
    {
        if (file.mimetype.indexOf('image') === -1) { // 현재 테스트를 이미지로만 할꺼기에 이미지로 세팅.
            //req.validateErr = '<script>alert("이미지 파일만 업로드 가능합니다."); location.replace("/single");</script>';
            //callback(null, false, new Error('이미지 파일만 업로드 가능합니다.'));
            callback(null, false);
        } else {
            callback(null, true);
        }
    }
});
router.use(express.static('public/upload'));

router.get('/',function (req,res) {
    res.render('submit');
});

router.post('/receive',upload.single('userfile'),function (req,res) {
    //console.log(req.file);
    var uploadFolder = './public/upload/'
    fs.readdir(uploadFolder,function(error,_filelist){
        //console.log(_filelist.length);
        console.log(req.file);

        if(req.file != undefined)
        {
            res.render('receive', {
                filename: req.file.originalname,
                filenamedir: req.file.originalname,
                length: _filelist.length,
                filelist: _filelist
            });
        }
        else{
            res.render('receive', {
                filenamedir: "../images/white.jpg",
                filename : "did not submit! or wrong file type!",
                length: _filelist.length,
                filelist: _filelist
            });
        }

    })

    /*
    res.send(`<link rel='stylesheet' href='/stylesheets/style.css' />
    당신이 제출한 사진은 <br> 
    uploaded : ${req.file.originalname} <br><br> 
    <img src="../${req.file.originalname}" width="192" height="108">`
    );
    */
});


module.exports = router;