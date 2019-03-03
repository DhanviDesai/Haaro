const apiCallFromRequest = require('./Request')
const apiCallFromNode = require('./NodeJsCall')

const http = require('http')

http.createServer((req, res) => {
        if(req.url === "/request"){
            apiCallFromRequest.callApi(function(response){
                //console.log(JSON.stringify(response));
                res.write(JSON.stringify(response));
                res.end();
            });
        }
        else if(req.url === "/node"){
            apiCallFromNode.callApi(function(response){
                res.write(response);
                res.end();
            });
        }
        
        // res.end();
}).listen(3000);

console.log("service running on 3000 port....");

/*

const apiCallFromRequest = require('./Request');
const apiCallFromNode = require('./NodeJsCall');
const Joi = require('joi');
const express = require('express');
const app = express();

app.use(express.json());


const courses = [
    {
        id : 1,
        name: 'course 1'
    },
    {
        id : 2,
        name: 'course 2'
    },
    {
        id : 3,
        name: 'course 3'
    }

];

app.get('/',(req,res) => {

    res.send('Hellow world');
    
});

app.get('/api/json',(req,res) => {
   apiCallFromNode.callApi(function(response){
        res.write(response);
        res.end();
    });
});




app.post('/api/courses',(req,res) =>{

    const schema = {
        name: Joi.string().min(3).required()
    };

    const result = Joi.validate(req.body,schema);

    if(result.error){
        res.status(404).send(result.error.details[0].message);
        return; 
    }

    const course = {
       id: courses.length + 1,
       name: req.body.name      
    };

    courses.push(course);
    res.send(course);
});


app.put('/api/courses/:id',(req,res) => {

    const course =  courses.find(c => c.id === parseInt(req.params.id));
 if(!course) res.status(404).send('The course with the given ID not fond');

 
const result  = validatecourse(req.body);
if(result.error){
    res.status(404).send(result.error.details[0].message);
    return; 
}

course.name = req.body.name;
res.send(course);

});


function validatecourse(course){
    const schema = {
        name: Joi.string().min(3).required()
    };
    
     return Joi.validate(course,schema);
}

app.get('/api/post/:id',(req,res) => {
 const course =  courses.find(c => c.id === parseInt(req.params.id));
 if(!course) res.status(404).send('The course with the given ID not fond');
 res.send(course);
});

const port = process.env.PORT || 3000;
app.listen(port,() => console.log(`Listening on port ${port}`));

*/