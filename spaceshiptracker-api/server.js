var express = require('express');
var app = express();
var bodyParser = require('body-parser');
var mongoose   = require('mongoose');
var cors   = require('cors');

var http = require('http').Server(app);

var io = require('socket.io')(http);



// configure app to use bodyParser()
// this will let us get the data from a POST
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Must be used for cross domain ajaxs calls.
// Adds access-control-allow-origin:*
var corsOptions = {
  origin: 'http://spaceshiptracker-glenngbg.c9users.io:8080',
  credentials : true
};
app.use(cors(corsOptions));

//crepidoinspace-johancn87.c9users.io:*
//io.set( 'origins', 'http://crepidoinspace-johancn87.c9users.io:8081' );

// Sets upp use of env variable or uses localhsot if not set
var dburl = process.env.dburl;
mongoose.connect(dburl | 'mongodb://mongo:27017/spacetracker');

// Data schema for REST input and persistance
var Position = require('./models/position');
var Image = require('./models/image');


var router = express.Router();   

app.use(express.static(__dirname + '/wwwroot'));
app.use('/js/cesium', express.static(__dirname + '/bower_components/cesium/Cesium'));

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
            console.log("Broadcasting");
            io.emit('Position_stored', position);
            
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
    

router.route('/images')
    // POST handler for storing of positions
    .post(function(req, res) {
        
        var image = new Image();     
        image.imageBytes = req.query.b; 
      
        image.timestamp = Date.now();

        image.save(function(err) {
            if (err)
                res.send(err);
            
            
            console.log("Image stored in db");
            console.log("Broadcasting");
            io.emit('NewImage', image);
            
            res.json({ message: 'Image stored!' });
            
            
        });
        
    })
    
    .get(function(req, res) {
        Image.find(function(err, images) {
            if (err)
                res.send(err);

            res.json(images);
        });
    });



//Socker handling
io.on('connection', function(socket){
  console.log('a user connected');
  
  socket.on('disconnect', function(){
    console.log('user disconnected');
  });
  
});


// REGISTER OUR ROUTES -------------------------------
// all of our routes will be prefixed with /api
app.use('/api', router);

// Starts the server on env variable PORT or 8080 if missing
var port = process.env.PORT || 8080;  


http.listen(port);
//app.listen(port);


console.log('Server is started on port ' + port);