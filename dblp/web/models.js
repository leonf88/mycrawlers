var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost:27017/dblp', {
  useMongoClient: true,
  promiseLibrary: global.Promise
});
var models = {};

models.article_model = mongoose.model("article", {
  title: 'string',
  link: 'string',
  year: 'string',
  author: 'string',
  abstract: 'string',
  biburl: 'string',
  _hook: 'string',
  _pname: 'string',
  _dname: 'string',
  _type: 'string',
  _key: 'string',
}, "dblp");

models.top_list_model = mongoose.model("top_list", {
  conferences: [],
  journals: []
}, 'dblp');

models.conf_list_model = mongoose.model("conf_list", {
  dname: 'string',
  data: []
}, 'dblp');

models.proceeding_model = mongoose.model("proceeding", {
  data: {}
}, 'dblp');

module.exports = models;
