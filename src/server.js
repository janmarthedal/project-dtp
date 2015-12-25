import express from 'express';
import bodyParser from 'body-parser';
import fs from 'fs';
import http from 'http';
import consolidate from 'consolidate';
import handlebars from 'handlebars';
import Promise from 'promise';
import React from 'react';
import ReactDOMServer from 'react-dom/server';
import EditItemForm from './edit-item-form';
import RenderItemBox from './render-item-box';
import {textToItemData} from './item-data';

var app = express(),
    base_dir = __dirname + '/..',
    create_types = {'definition': 'Definition', 'theorem': 'Theorem'};

['header', 'footer'].forEach(function (name) {
    var content = fs.readFileSync(base_dir + '/views/' + name + '.html', 'utf8');
    handlebars.registerPartial(name, handlebars.compile(content));
});

function post_json(host, port, path, data) {
    return new Promise(function (resolve, reject) {
        var postData = JSON.stringify(data);

        var options = {
            hostname: host,
            port: port,
            path: path,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': postData.length
            }
        };

        var req = http.request(options, function(res) {
            var body = '';
            if (res.statusCode >= 200 && res.statusCode < 300) {
                res.setEncoding('utf8');
                res.on('data', function (chunk) {
                    body += chunk;
                });
                res.on('end', function() {
                    try {
                        resolve(JSON.parse(body));
                    } catch (ex) {
                        reject(ex);
                    }
                });
            } else
                reject();
        });

        req.on('error', function(e) {
          reject();
        });

        req.write(postData);
        req.end();
    });
}

app.engine('html', consolidate.handlebars);
app.set('view engine', 'html');
app.set('views', base_dir + '/views');
app.use(bodyParser.urlencoded({extended: true}));
app.use('/static', express.static(base_dir + '/static'));

app.get('/', function(req, res) {
    res.render('home');
});
app.get('/create/:type', function(req, res) {
    if (req.params.type in create_types) {
        res.render('create', {
            title: 'New ' + create_types[req.params.type],
            extrajs: ['create'],
            editItemForm: ReactDOMServer.renderToString(<EditItemForm />),
        });
    } else
        res.sendStatus(400);
});
app.post('/create/:type', function(req, res) {
    if (req.params.type in create_types) {
        post_json('localhost', 8000, '/api/drafts/', {
            type: req.params.type,
            body: req.body
        }).then(function (result) {
            console.log('Created draft', result.id);
            res.redirect('/');
        }).catch(function () {
            res.sendStatus(500);
        });
    } else
        res.sendStatus(400);
});
app.get('/show', function(req, res) {
    var data = textToItemData('foobar');
    res.render('show', {
        title: 'Show Item',
        showItem: ReactDOMServer.renderToStaticMarkup(
            <RenderItemBox data={data} />
        ),
    });
});

app.listen(3000);
console.log('Listening on port 3000');
