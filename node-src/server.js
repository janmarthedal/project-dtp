import express from 'express';
import bodyParser from 'body-parser';

import eqn_typeset from './eqn-typeset';
import item_dom_to_html from './item-dom-to-html';
import markdown_to_item_dom from './markdown-to-item-dom';
import {object_to_array, array_to_object} from './pure-fun';

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
            const typeset_jobs = object_to_array(item_dom.eqns || {})
                .map(item => eqn_typeset(item[0], item[1]));
            return Promise.all(typeset_jobs)
                .then(eqn_list => ({
                    document: item_dom.document,
                    eqns: array_to_object(eqn_list)
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
        item_dom_to_html(req.body.document, req.body.eqns).then(html => {
            json_response(res, {html});
        });
    } else {
        res.status(400).send('Malformed data');
    }
});

app.listen(3000, function () {
  console.log('Listening on port 3000');
});
