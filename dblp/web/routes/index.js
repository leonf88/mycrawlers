var express = require('express');
var article_model = require('../models')
var router = express.Router();

/* GET home page. */
router.get('/', function(req, res, next) {
  article_model.distinct("_dname", {
    "_type": "journal"
  }, function(err, journal_list) {
    if (err) return handleError(err);
    article_model.distinct("_dname", {
      "_type": "conference"
    }, function(err, conference_list) {
      if (err) return handleError(err);

      conference_list.sort();
      journal_list.sort();
      res.render('index', {
        conference_list: conference_list,
        journal_list: journal_list
      });
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

  article_model.distinct("_pname", {
    "_dname": req.params.dname,
    "_type": type
  }, function(err, pnames) {
    if (err) return handleError(err);

    pnames.sort();
    res.render('dlist', {
      pnames: pnames,
      type: req.params.type,
      dname: req.params.dname
    });
  })
});

router.get('/:type/:dname/:pname', function(req, res, next) {
  var type = null;
  if (req.params.type == "conf") {
    type = "conference";
  } else if (req.params.type == "jour") {
    type = "journal";
  }

  article_model.find({
    "_dname": req.params.dname,
    "_pname": req.params.pname,
    "_type": type
  }, function(err, data) {
    if (err) return handleError(err);

    res.render('plist', {
      type: req.params.type,
      dname: req.params.dname,
      pname: req.params.pname,
      data: data
    });
  })
});

module.exports = router;
