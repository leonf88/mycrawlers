var mongoose = require('mongoose');
mongoose.connect('mongodb://localhost:27017/dblp', {
  useMongoClient: true,
  promiseLibrary: global.Promise
});

var article_model = mongoose.model("article", {
  title: 'string',
  link: 'string',
  year: 'string',
  author: 'string',
  _pname: 'string',
  _dname: 'string',
  _type: 'string',
}, "dblp")

module.exports = article_model
