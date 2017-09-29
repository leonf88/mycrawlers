var express = require('express');
var models = require('../models')
var router = express.Router();
var exec = require('child_process').exec, child;

/* GET home page. */
router.get('/', function(req, res, next) {
  models.top_list_model.findOne({
    "_key": "top_list"
  }, function(err, data) {
    if (err) return handleError(err);
    conference_list = data.conferences;
    journal_list = data.journals;
    res.render('index', {
      conference_list: conference_list,
      journal_list: journal_list
    });
  });
});

router.get('/:type/:dname', function(req, res, next) {
  var type = null;
  if (req.params.type == "conf") {
    type = "conference";
  } else if (req.params.type == "jour") {
    type = "journal";
  }
  models.conf_list_model.findOne({
    "_key": "conf_list",
    "dname": req.params.dname
  }, function(err, data) {
    if (err) return handleError(err);
    res.render('dlist', {
      pnames: data['data'],
      type: req.params.type,
      dname: req.params.dname
    });
  });
});


router.get('/:type/:dname/:pname', function(req, res, next) {
  var type = null;
  if (req.params.type == "conf") {
    type = "conference";
  } else if (req.params.type == "jour") {
    type = "journal";
  }
  models.proceeding_model.findOne({
    "_key": "conf_proceeding",
    "_dname": req.params.dname,
    "_pname": req.params.pname,
    "_type": type
  }, function(err, proceeding) {
    if (err) return handleError(err);
    models.article_model.find({
      "_dname": req.params.dname,
      "_pname": req.params.pname,
      "_type": type
    }, function(err, array) {
      var m = {}
      for (const e of array) {
        m[e._hook] = e
      }
      for (let s of proceeding.data) {
        for (let e of s['articles']) {
          var h = e['_hook'];
          for (const k in m[h]) {
            e[k] = m[h][k];
          }
        }
      }
      res.render('plist', {
        type: req.params.type,
        dname: req.params.dname,
        pname: req.params.pname,
        data: proceeding.data
      });
    });
  });
});

router.post('/update_abstract/:hook', function(req, res, next) {
  exec('',
    function(error, stdout, stderr) {
      console.log('stdout: ' + stdout);
      console.log('stderr: ' + stderr);
      if (error !== null) {
        console.log('exec error: ' + error);
      }
    })();
})

module.exports = router;
