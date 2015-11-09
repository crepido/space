var express = require("express");

var app = express();

app.use(express.static(__dirname + '/wwwroot'));
app.use('/js/cesium', express.static(__dirname + '/bower_components/cesium/Cesium'));



app.listen(8081, function() { console.log('listening!')});