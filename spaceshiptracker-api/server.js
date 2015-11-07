var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var mongoose   = require('mongoose');

// configure app to use bodyParser()
// this will let us get the data from a POST
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

var dburl = process.env.dburl;

mongoose.connect(dburl);

var Position = require('./models/position');

var port = process.env.PORT || 8080;  

var router = express.Router();   

// middleware to use for all requests
router.use(function(req, res, next) {
    // do logging
    console.log('Something is happening.');
    next(); // make sure we go to the next routes and don't stop here
});

// test route to make sure everything is working (accessed at GET http://localhost:8080/api)
router.get('/', function(req, res) {
    res.json({ message: 'Spaceshiptracker API' });   
});

router.route('/positions')
    .post(function(req, res) {
        
        var position = new Position();     
        position.lat = req.query.lat; 
        position.lon = req.query.lon; 
        position.alt = req.query.alt; 
        position.ship = req.query.ship; 
        position.timestamp = Date.now();

        position.save(function(err) {
            if (err)
                res.send(err);
            
            console.log(position);
            console.log("Position stored in db");
            res.json({ message: 'Position stored!' });
        });
        
    })
    
    .get(function(req, res) {
        Position.find(function(err, positions) {
            if (err)
                res.send(err);

            res.json(positions);
        });
    });
    
router.route('/positions/:shipname')

    // get the bear with that id (accessed at GET http://localhost:8080/api/bears/:bear_id)
    .get(function(req, res) {
        Position.find({ ship: req.params.shipname }, function(err, positions) {
            if (err)
                res.send(err);
            res.json(positions);
        });
    });



// REGISTER OUR ROUTES -------------------------------
// all of our routes will be prefixed with /api
app.use('/api', router);

// START THE SERVER
// =============================================================================
app.listen(port);
console.log('Magic happens on port ' + port);

function getDateTime() {

    var date = new Date();

    var hour = date.getHours();
    hour = (hour < 10 ? "0" : "") + hour;

    var min  = date.getMinutes();
    min = (min < 10 ? "0" : "") + min;

    var sec  = date.getSeconds();
    sec = (sec < 10 ? "0" : "") + sec;

    var year = date.getFullYear();

    var month = date.getMonth() + 1;
    month = (month < 10 ? "0" : "") + month;

    var day  = date.getDate();
    day = (day < 10 ? "0" : "") + day;

    return year + ":" + month + ":" + day + ":" + hour + ":" + min + ":" + sec;

}