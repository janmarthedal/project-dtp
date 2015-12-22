import express from 'express';
import bodyParser from 'body-parser';
import fs from 'fs';
import consolidate from 'consolidate';
import handlebars from 'handlebars';
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
        res.sendStatus(404);
});
app.post('/create/:type', function(req, res) {
    if (req.params.type in create_types) {
        console.log(req.body);
        res.redirect('/');
    } else
        res.sendStatus(404);
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
