var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var mongoose   = require('mongoose');
var cors   = require('cors');

// configure app to use bodyParser()
// this will let us get the data from a POST
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Must be used for cross domain ajaxs calls.
// Adds access-control-allow-origin:*
app.use(cors());

// Sets upp use of env variable or uses localhsot if not set
var dburl = process.env.dburl;
mongoose.connect(dburl | 'mongodb://mongo:27017/spacetracker');

// Data schema for REST input and persistance
var Position = require('./models/position');


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
    // POST handler for storing of positions
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
    
    // Gets all positions for all ships
    .get(function(req, res) {
        Position.find(function(err, positions) {
            if (err)
                res.send(err);

            res.json(positions);
        });
    });
    
// Gets all positions for specified ship
// domain.com/api/poisitons/shipname
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

// Starts the server on env variable PORT or 8080 if missing
var port = process.env.PORT || 8080;  
app.listen(port);

console.log('Server is started on port ' + port);