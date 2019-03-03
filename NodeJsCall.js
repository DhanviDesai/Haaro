var myModule = require('./index');
const https = require('https');
const http = require('http');

   


const callExternalApiUsingHttp = (callback) => {

    const val = myModule.path;
    const sub = myModule.sub;

    console.log(val);
    var _EXTERNAL_URL = "http://127.0.0.1:6942/api/airports?location="+val+"&sub="+sub;
    

    http.get(_EXTERNAL_URL, (resp) => {
    let data = '';
    
    // A chunk of data has been recieved.
    resp.on('data', (chunk) => {
        data += chunk;
    });
    
    // The whole response has been received. Print out the result.
    resp.on('end', () => {

        return callback(data);
        
    });
    
    }).on("error", (err) => {
       
    console.log("Error: " + err.message);
    });
}


const callExternalApiUsingHttp1 = (callback) => {

    const val = myModule.path;

    console.log(val);
    var _EXTERNAL_URL = `https://v4p4sz5ijk.execute-api.us-east-1.amazonaws.com/anbdata/states/notams/notams-list?format=json&api_key=9d849040-30e7-11e9-9872-b90b55b59c3d&states=IND`;
    

    https.get(_EXTERNAL_URL, (resp) => {
    let data = '';
    
    // A chunk of data has been recieved.
    resp.on('data', (chunk) => {
        data += chunk;
    });
    
    // The whole response has been received. Print out the result.
    resp.on('end', () => {

        return callback(data);
        
    });
    
    }).on("error", (err) => {
       
    console.log("Error: " + err.message);
    });
}



const callExternalApiUsingHttp3 = (callback) => {

    const val = myModule.path;

    console.log(val);

    var _EXTERNAL_URL = `http://100.192.0.67:5000/lazy2/IND/${val}/airport`;
    

    http.get(_EXTERNAL_URL, (resp) => {
    let data = '';
    
    // A chunk of data has been recieved.
    resp.on('data', (chunk) => {
        data += chunk;
    });
    
    // The whole response has been received. Print out the result.
    resp.on('end', () => {

        return callback(data);
        
    });
    
    }).on("error", (err) => {
       
    console.log("Error: " + err.message);
    });
}

const callExternalApiUsingHttp4 = (callback) => {

    const val = myModule.path;
    const sub = myModule.sub;


    console.log(val);

    var _EXTERNAL_URL = `http://100.192.0.67:5000/lazy22/IND/${val}/airport?sub=${sub}`;
    

    http.get(_EXTERNAL_URL, (resp) => {
    let data = '';
    
    // A chunk of data has been recieved.
    resp.on('data', (chunk) => {
        data += chunk;
    });
    
    // The whole response has been received. Print out the result.
    resp.on('end', () => {

        return callback(data);
        
    });
    
    }).on("error", (err) => {
       
    console.log("Error: " + err.message);
    });
}



module.exports.callApi = callExternalApiUsingHttp;
module.exports.callApi1 = callExternalApiUsingHttp1;
module.exports.callApi11 = callExternalApiUsingHttp3;
module.exports.callApi111 = callExternalApiUsingHttp4;

