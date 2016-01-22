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

const base_dir = __dirname + '/..',
    definition_slug = 'definition',
    theorem_slug = 'theorem',
    create_types = {};

create_types[definition_slug] = {
    title: 'Definition',
    db_type: DataStore.DEFINITION
};

create_types[theorem_slug] = {
    title: 'Theorem',
    db_type: DataStore.THEOREM
};

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
    console.log('Initializing handlebars');
    return Promise.all(['header', 'footer'].map(load_handlebars_partial));
}

class Router {
    constructor() {
        this._views = {};
    }
    add(method, url, view, name) {
        this._views[name] = {view, url, method};
    }
    reverse(name, params) {
        return this._views[name].url.replace(/:([a-z_]+)/g, (_, p) => params[p]);
    }
    init_express(app) {
        for (let name in this._views) {
            const data = this._views[name];
            app[data.method](data.url, data.view);
        }
    }
}

const router = new Router();

function views_home(req, res) {
    res.render('home', {
        linkCreateDefinition: router.reverse('draft-create', {type: definition_slug}),
        linkCreateTheorem: router.reverse('draft-create', {type: theorem_slug}),
    });
}

function views_create_draft(req, res) {
    if (req.params.type in create_types) {
        res.render('create', {
            title: 'New ' + create_types[req.params.type].title,
            extrajs: ['create'],
            editItemForm: ReactDOMServer.renderToString(<EditItemForm />),
        });
    } else
        res.sendStatus(400);
}

function views_create_draft_post(req, res) {
    if (req.params.type in create_types) {
        const item_type = create_types[req.params.type].db_type,
            body = req.body.body;
        datastore.create_draft(item_type, body).then(id => {
            console.log('Created draft', create_types[req.params.type].title, id);
            res.redirect('/');
        }).catch(err => {
            console.log('Error creating draft', err);
            res.sendStatus(500);
        });
    } else
        res.sendStatus(400);
}

function views_show_draft(req, res) {
    const data = textToItemData('foobar');
    res.render('show', {
        title: 'Show Item',
        showItem: ReactDOMServer.renderToStaticMarkup(
            <RenderItemBox data={data} />
        ),
    });
}

function setup_express(datastore) {
    console.log('Initializing express');

    const app = express();
    app.engine('html', consolidate.handlebars);
    app.set('view engine', 'html');
    app.set('views', base_dir + '/views');
    app.use(bodyParser.urlencoded({extended: true}));
    app.use('/static', express.static(base_dir + '/static'));

    router.add('get', '/', views_home, 'home');
    router.add('get', '/create/:type', views_create_draft, 'draft-create');
    router.add('post', '/create/:type', views_create_draft_post, 'draft-create-post');
    router.add('get', '/show', views_show_draft, 'draft-show');
    router.init_express(app);

    app.listen(3000);

    return 3000;
}

function create_datastore() {
    console.log('Initializing data store');
    var datastore = new DataStore();
    return datastore.init().then(() => datastore);
}

Promise.resolve(true).then(
    setup_handlebars
).then(
    create_datastore
).then(
    datastore => {
        const port = setup_express(datastore);
        console.log('Listening on port ' + port);
    }
);
