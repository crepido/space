var mongoose     = require('mongoose');
var Schema       = mongoose.Schema;

var ImageSchema   = new Schema({
    imageBytes: String,
    timestamp: Date
});

module.exports = mongoose.model('Image', ImageSchema);