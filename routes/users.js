var express = require('express');
var router = express.Router();

router.use(express.static('public/images'));

/* GET users listing. */
router.get('/', function(req, res, next) {
  res.send('Hello users, <img src="iu.jpg">');
});
module.exports = router;
