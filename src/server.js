import express from 'express';
import bodyParser from 'body-parser';
import fs from 'fs';
import http from 'http';
import consolidate from 'consolidate';
import handlebars from 'handlebars';
import Promise from 'promise';
import React from 'react';
import ReactDOMServer from 'react-dom/server';

import EditItemBox from './edit-item-box';
import RenderItemBox from './render-item-box';
import {textToItemData, itemDataToHtml} from './item-data';
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

function item_type_title(item) {
    for (let slug in create_types) {
        const ct = create_types[slug];
        if (ct.db_type === item.item_type)
            return ct.title;
    }
    throw new Error('item_type_title');
}

function draft_title(item) {
    return item_type_title(item) + ' ' + item.id;
}

function mathitem_slug(item) {
    return item.item_type + item.id;
}

function mathitem_title(item) {
    return item_type_title(item) + ' ' + mathitem_slug(item);
}

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

function views_home(req, res) {
    req.datastore.get_mathitem_list().then(items => {
        res.render('home', {
            items: items.map(item => ({
                name: mathitem_title(item),
                link: req.router.reverse('mathitem-show', {slug: mathitem_slug(item)})
            })),
            linkDrafts: req.router.reverse('drafts-home'),
            linkCreateDefinition: req.router.reverse('draft-create', {type: definition_slug}),
            linkCreateTheorem: req.router.reverse('draft-create', {type: theorem_slug}),
        });
    });
}

function views_drafts(req, res) {
    req.datastore.get_draft_list().then(drafts => {
        res.render('drafts', {
            items: drafts.map(item => ({
                name: draft_title(item),
                link: req.router.reverse('draft-show', {id: item.id})
            })),
        });
    });
}

function views_show_draft(req, res) {
    req.datastore.get_draft(req.params.id).then(item => {
        const data = textToItemData(item.body);
        const html = itemDataToHtml(data);
        res.render('show', {
            title: draft_title(item),
            notes: item.notes,
            showItem: ReactDOMServer.renderToStaticMarkup(<RenderItemBox html={html} />),
            linkEdit: req.router.reverse('draft-edit', {id: item.id}),
        });
    });
}

function views_show_mathitem(req, res) {
    const match = req.params.slug.match(/([DTP])([1-9][0-9]*)/);
    if (!match) {
        res.sendStatus(404);
        return;
    }
    req.datastore.get_mathitem(match[2]).then(item => {
        if (item.item_type === match[1]) {
            const data = textToItemData(item.body);
            const html = itemDataToHtml(data);
            res.render('show-mathitem', {
                title: mathitem_title(item),
                showItem: ReactDOMServer.renderToStaticMarkup(<RenderItemBox html={html} />),
            });
        } else {
            res.sendStatus(404);
        }
    });
}

function views_show_draft_post(req, res) {
    console.log(req.body);
    if ('delete' in req.body) {
        req.datastore.delete_draft(req.params.id).then(() => {
            res.redirect(req.router.reverse('drafts'));
        });
    } else if ('publish' in req.body) {
        const draft_id = req.params.id;
        req.datastore.get_draft(draft_id).then(
            draft => req.datastore.create_mathitem(draft.item_type, draft.body)
        ).then(
            item_id => req.datastore.delete_draft(draft_id).then(() => item_id)
        ).then(
            item_id => {
                console.log('Item id', item_id);
                res.redirect(req.router.reverse('home'));
            }
        );
    } else
        res.sendStatus(400);
}

function views_create_draft(req, res) {
    if (req.params.type in create_types) {
        res.render('edit', {
            title: 'New ' + create_types[req.params.type].title,
            extrajs: ['edit'],
            notes: 'Some note',
            editItemBox: ReactDOMServer.renderToStaticMarkup(<EditItemBox />),
            renderItemBox: ReactDOMServer.renderToStaticMarkup(<RenderItemBox  />),
            linkCancel: req.router.reverse('home')
        });
    } else
        res.sendStatus(400);
}

function views_create_draft_post(req, res) {
    if (req.params.type in create_types) {
        const item_type = create_types[req.params.type].db_type,
            body = req.body.body,
            notes = req.body.notes;
        req.datastore.create_draft(item_type, body, notes).then(id => {
            console.log('Created draft', create_types[req.params.type].title, id);
            res.redirect(req.router.reverse('draft-show', {id}));
        }).catch(err => {
            console.log('Error creating draft', err);
            res.sendStatus(500);
        });
    } else
        res.sendStatus(400);
}

function views_edit_draft(req, res) {
    req.datastore.get_draft(req.params.id).then(item => {
        res.render('edit', {
            title: 'Edit ' + draft_title(item),
            extrajs: ['edit'],
            notes: item.notes,
            editItemBox: ReactDOMServer.renderToStaticMarkup(<EditItemBox initBody={item.body} />),
            renderItemBox: ReactDOMServer.renderToStaticMarkup(<RenderItemBox  />),
            linkCancel: req.router.reverse('draft-show', {id: req.params.id})
        });
    }).catch(() => res.sendStatus(404));
}

function views_edit_draft_post(req, res) {
    req.datastore.update_draft(req.params.id, req.body.body, req.body.notes).then(() => {
        console.log('Updated draft', req.params.id);
        res.redirect(req.router.reverse('draft-show', {id: req.params.id}));
    }).catch(err => {
        console.log('Error updating draft', err);
        res.sendStatus(500);
    });
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

    router.add('get', '/', views_home, 'home');
    router.add('get', '/drafts/', views_drafts, 'drafts-home');
    router.add('get', '/drafts/:id', views_show_draft, 'draft-show');
    router.add('post', '/drafts/:id', views_show_draft_post, 'draft-show-post');
    router.add('get', '/create/:type', views_create_draft, 'draft-create');
    router.add('post', '/create/:type', views_create_draft_post, 'draft-create-post');
    router.add('get', '/drafts/:id/edit', views_edit_draft, 'draft-edit');
    router.add('post', '/drafts/:id/edit', views_edit_draft_post, 'draft-edit-post');
    router.add('get', '/items/:slug', views_show_mathitem, 'mathitem-show');
    router.init_express(app);

    app.listen(port);
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
        const port = 3000;
        setup_express(datastore, port);
        console.log('Listening on port ' + port);
    }
).catch(err => {
    console.log('Fail during initialization', err);
});
