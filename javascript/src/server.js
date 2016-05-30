import express from 'express';
import bodyParser from 'body-parser';
import {fromPairs, map} from 'lodash';

import eqn_typeset from './eqn-typeset';
import item_dom_to_html from './item-dom-to-html';
import markdown_to_item_dom from './markdown-to-item-dom';

function json_response(res, data) {
    res.setHeader('Content-Type', 'application/json');
    res.send(JSON.stringify(data));
}

var app = express();

app.use(bodyParser.json());

app.get('/', function (req, res) {
    json_response(res, {'ok': true});
});

app.post('/prepare-item', function(req, res) {
    if (req.body.text) {
        markdown_to_item_dom(req.body.text).then(item_dom => {
            const typeset_jobs = map(item_dom.eqns || {},
                                     (data, key) => eqn_typeset(key, data));
            return Promise.all(typeset_jobs)
                .then(eqn_list => ({
                    document: item_dom.document,
                    tags: item_dom.tags,
                    eqns: fromPairs(eqn_list),
                }));
        }).then(result => {
            json_response(res, result);
        });
    } else {
        res.status(400).send('Malformed data')
    }
});

app.post('/render-item', function(req, res) {
    if (req.body.document) {
        item_dom_to_html(req.body.document, req.body.eqns, req.body.tags).then(data => {
            json_response(res, data);
        });
    } else {
        res.status(400).send('Malformed data');
    }
});

app.listen(3000, function () {
  console.log('Listening on port 3000');
});
