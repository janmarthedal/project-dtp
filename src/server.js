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
import DataStore from './data-store';

const base_dir = __dirname + '/..';

function load_handlebars_partial(name) {
    new Promise((resolve, reject) => {
        fs.readFile(base_dir + '/views/' + name + '.html', 'utf8', (err, content) => {
            if (err) {
                reject(err);
                return;
            }
            handlebars.registerPartial(name, handlebars.compile(content));
            resolve();
        })
    });
}

function setup_handlebars() {
    return Promise.all(['header', 'footer'].map(load_handlebars_partial));
}

function setup_express() {
    const create_types = {'definition': 'Definition', 'theorem': 'Theorem'};
    var app = express();

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

    return 3000;
}

Promise.resolve(true).then(() => {
    console.log('Initializing handlebars');
    return setup_handlebars();
}).then(() => {
    var datastore = new DataStore();
    console.log('Initializing data store');
    return datastore.init();
}).then(() => {
    console.log('Initializing express');
    return setup_express();
}).then(port =>
    console.log('Listening on port ' + port)
);
