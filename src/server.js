import express from 'express';
import bodyParser from 'body-parser';
import fs from 'fs';
import http from 'http';
import consolidate from 'consolidate';
import handlebars from 'handlebars';
import DataStore from './data-store';
import * as views from './views';

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

function setup_express(datastore, port) {
    console.log('Initializing express');

    const app = express();
    const router = new Router();

    app.engine('html', consolidate.handlebars);
    app.set('view engine', 'html');
    app.set('views', base_dir + '/views');
    app.use(bodyParser.urlencoded({extended: true}));
    app.use('/static', express.static(base_dir + '/static'));

    app.all('*', (req, res, next) => {
        req.datastore = datastore;
        req.router = router;
        next();
    });

    router.add('get', '/', views.home, 'home');
    router.add('get', '/drafts/', views.drafts, 'drafts-home');
    router.add('get', '/drafts/:id', views.show_draft, 'draft-show');
    router.add('post', '/drafts/:id', views.show_draft_post, 'draft-show-post');
    router.add('get', '/create/:type', views.create_draft, 'draft-create');
    router.add('post', '/create/:type', views.create_draft_post, 'draft-create-post');
    router.add('get', '/drafts/:id/edit', views.edit_draft, 'draft-edit');
    router.add('post', '/drafts/:id/edit', views.edit_draft_post, 'draft-edit-post');
    router.add('get', '/items/:slug', views.show_mathitem, 'mathitem-show');
    router.init_express(app);

    app.listen(port);
}

function create_datastore() {
    console.log('Initializing data store');
    var datastore = new DataStore();
    return datastore.init().then(() => datastore);
}

Promise.resolve(true)
    .then(setup_handlebars)
    .then(create_datastore)
    .then(datastore => {
        const port = 3000;
        setup_express(datastore, port);
        console.log('Listening on port ' + port);
    })
    .catch(err => {
        console.log('Error during initialization', err);
    });
