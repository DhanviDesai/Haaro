const apiCallFromRequest = require('./Request');
const apiCallFromNode = require('./NodeJsCall');
const Joi = require('joi');
const express = require('express');
const app = express();
app.use( express.static( "public" ) );
app.set('view engine','ejs');

const MongoClient = require('mongodb').MongoClient;
const url = "mongodb://localhost:27017/mydb";

app.use(express.json());


app.get('/login',(req,res) => {

  res.render('login');

  
});

app.get('/',(req,res) => {

    res.render('home_new');

    
});


app.get('/api',(req,res) => {

    var temp = req.query;
    var path = temp.location;

    var sub;
    if(typeof req.query.sub != 'undefined') {
      sub = temp.sub;
    } else {
      sub = "ALL";
    }
    var tt="";
   
    console.log(sub);

    exports.path = path;
    exports.sub = sub;

    apiCallFromNode.callApi(function(response){

        var resultobj = JSON.parse(response);
        console.log(resultobj);
        console.log("======");
        console.log(resultobj.data);
        console.log("======");

        res.render('airport',{ data : resultobj["data"], sub: sub, icao_code : resultobj["code"], path : path, unique_subjects:resultobj["unique_subjects"] });
    });
    
   
});

app.get('/mapview',(req,res) => {
      res.render('mapview');
});


app.get('/analytics',(req,res) => {
  res.render('analytics');
});




app.get('/prabhu',(req,res) => {

  var temp = req.query;
    var status = temp.status;
    var icao = temp.icao;
    var subject = temp.subject;
res.render('tempmap',{status: status, icao: icao, subject: subject,coord1:"null",coord2:"null"});
});

app.get('/prabhuCoord',(req,res)=>{

  var temp = req.query;
    var status = temp.status;
    var icao = temp.icao;
    var subject = temp.subject;
    var coord1=temp.coord1;
    console.log(coord1);
    var coord2 = temp.coord2;
    console.log(coord2);
res.render('tempmap',{status: status, icao: icao, subject: subject,coord1:coord1,coord2:coord2});
});


app.get('/mapresult',(req,res) => {
  var temp = req.query;
    var path = temp.location;

    var sub;
    if(typeof req.query.sub != 'undefined') {
      sub = temp.sub;
    } else {
      sub = "ALL";
    }
    var tt="";
   
    console.log(sub);

    exports.path = path;
    exports.sub = sub;

      apiCallFromNode.callApi(function(response){

        var resultobj = JSON.parse(response);
        console.log(resultobj);
        console.log("======");
        console.log(resultobj);
        console.log("======");

        res.render('mapresult',{ data : resultobj["data"], sub: sub, icao_code : resultobj["code"], path : path, unique_subjects:resultobj["unique_subjects"] });
    });
});

app.get('/raw',(req,res) => {
  var temp = req.query;
    var path = temp.location;
    var sub;
    if(typeof req.query.sub != 'undefined') {
      sub = temp.sub;
    } else {
      sub = "ALL";
    }

    exports.path = path;
    exports.sub = sub;

      apiCallFromNode.callApi11(function(response){

        var resultobj = JSON.parse(response);
        console.log(resultobj);
        console.log("======");
        console.log(resultobj.subjects);
        console.log("======");

        res.render('rawnotam',{data:resultobj["notams"],path : path, sub: sub,unique_subjects:resultobj["subjects"]});
    });
});

app.get('/raw1',(req,res) => {
  var temp = req.query;
    var path = temp.location;
    sub = temp.sub;
    exports.path = path;
    exports.sub = sub;

      apiCallFromNode.callApi111(function(response){

        var resultobj = JSON.parse(response);
        console.log(resultobj);
        console.log("======");
        console.log(resultobj.subjects);
        console.log("======");

        res.render('rawnotam',{data:resultobj["notams"],path : path, sub: sub,unique_subjects:resultobj["subjects"]});
    });
});




const port = process.env.PORT || 3000;
app.listen(port,() => console.log(`Listening on port ${port}`));

