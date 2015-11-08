var mongoose     = require('mongoose');
var Schema       = mongoose.Schema;

var PositionSchema   = new Schema({
    lat: Number,
    lon: Number,
    alt: Number,
    ship: String,
    timestamp: Date
});

module.exports = mongoose.model('Position', PositionSchema);