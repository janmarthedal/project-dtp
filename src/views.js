import React from 'react';
import ReactDOMServer from 'react-dom/server';
import DataStore from './data-store';
import EditItemBox from './edit-item-box';
import RenderItemBox from './render-item-box';
import ItemDataInfoBox from './item-data-info-box';
import {textToItemData, itemDataToHtml} from './item-data';

const definition_slug = 'definition',
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

export function home(req, res) {
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

export function drafts(req, res) {
    req.datastore.get_draft_list().then(drafts => {
        res.render('drafts', {
            items: drafts.map(item => ({
                name: draft_title(item),
                link: req.router.reverse('draft-show', {id: item.id})
            })),
        });
    });
}

export function show_draft(req, res) {
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

export function show_mathitem(req, res) {
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

export function show_draft_post(req, res) {
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

export function create_draft(req, res) {
    if (req.params.type in create_types) {
        res.render('edit', {
            title: 'New ' + create_types[req.params.type].title,
            extrajs: ['edit'],
            notes: 'Some note',
            editItemBox: ReactDOMServer.renderToStaticMarkup(<EditItemBox />),
            renderItemBox: ReactDOMServer.renderToStaticMarkup(<RenderItemBox  />),
            itemDataInfoBox: ReactDOMServer.renderToStaticMarkup(<ItemDataInfoBox />),
            linkCancel: req.router.reverse('home')
        });
    } else
        res.sendStatus(400);
}

export function create_draft_post(req, res) {
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

export function edit_draft(req, res) {
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

export function edit_draft_post(req, res) {
    req.datastore.update_draft(req.params.id, req.body.body, req.body.notes).then(() => {
        console.log('Updated draft', req.params.id);
        res.redirect(req.router.reverse('draft-show', {id: req.params.id}));
    }).catch(err => {
        console.log('Error updating draft', err);
        res.sendStatus(500);
    });
}
