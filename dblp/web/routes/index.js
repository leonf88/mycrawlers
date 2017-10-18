var express = require('express');
var models = require('../models')
var router = express.Router();
var exec = require('child_process').exec,
  child;

function handleError(err, req, res, next) {
  res.status(500)
  res.render('error', {
    error: err
  })
}


/* GET home page. */
router.get('/', function(req, res, next) {
  models.top_list_model.findOne({
    "_key": "top_list"
  }, function(err, data) {
    if (err || ! data) return handleError(err, req, res, next);
    conference_list = data.conferences;
    journal_list = data.journals;
    res.render('index', {
      conference_list: conference_list,
      journal_list: journal_list
    });
  });
});

router.get('/db/:type/:dname', function(req, res, next) {
  var type = null;
  if (req.params.type == "conf") {
    type = "conference";
    key = "conf_list"
  } else if (req.params.type == "jour") {
    type = "journal";
    key = "jour_list"
  }
    console.log(req.params.dname)
  models.conf_list_model.findOne({
    "_key": key,
    "dname": req.params.dname
  }, function(err, data) {
    if (err) return handleError(err, req, res, next);
    if (data == null) return handleError(err, req, res, next);
    data['data'].sort(function(a, b) {
      return a['pname'] < b['pname']
    });
    res.render('dlist', {
      pnames: data['data'],
      type: req.params.type,
      dname: req.params.dname
    });
  });
});


router.get('/db/:type/:dname/:pname', function(req, res, next) {
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
    if (err) return handleError(err, req, res, next);
    models.article_model.find({
      "_dname": req.params.dname,
      "_pname": req.params.pname,
      "_type": type
    }, function(err, array) {
      if (proceeding == null) {
        return handleError(err, req, res, next);
      }
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

router.get('/update_abstract', function(req, res, next) {
  // res.json({"abstract": "hello"})
  var hook = req.query['hook']
  c = exec('cd ../crawler; scrapy crawl dblp_article -a hook=' + hook,
    function(error, stdout, stderr) {
      console.log('stdout: ' + stdout);
      console.log('stderr: ' + stderr);
      if (error !== null) {
        console.log('exec error: ' + error);
      } else {

      }
    });
  c.on('exit', function() {
    models.article_model.findOne({
      "_hook": hook
    }, function(err, article) {
      if (err) return handleError(err, req, res, next);
      res.json({
        "abstract": article['abstract']
      })
    });
  });
})

module.exports = router;
