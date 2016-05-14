'use strict';

var express = require('express');
var bodyParser = require('body-parser');
var mjAPI = require('mathjax-node/lib/mj-single.js');

mjAPI.config({MathJax: {}});
mjAPI.start();

function typeset(id, math, format) {
    if (['TeX', 'inline-TeX'].indexOf(format) < 0)
        return Promise.reject('illegal typeset format');
    return new Promise(function (resolve, reject) {
        console.log('Typesetting: ' + math);
        mjAPI.typeset({
            math: math,
            format: format,
            html: true,
        }, function (data) {
            if (data.errors) {
                reject(data.errors);
            } else {
                resolve({
                    id: id,
                    html: data.html
                });
            }
        });
    });
}

function json_response(res, data) {
    res.setHeader('Content-Type', 'application/json');
    res.send(JSON.stringify(data));
}

var app = express();

app.use(bodyParser.json());

app.get('/', function (req, res) {
    json_response(res, {'ok': true});
});

app.post('/typeset', function(req, res) {
    if (!req.body.eqns) {
        res.status(400).send('Malformed data')
        return;
    }
    Promise.all(req.body.eqns.map(function (item) {
        return typeset(item.id, item.math, item.format);
    })).then(function (results) {
        json_response(res, results);
    }, function (err) {
        res.status(500).send('typeset error');
    });
});

app.listen(3000, function () {
  console.log('Listening on port 3000');
});
