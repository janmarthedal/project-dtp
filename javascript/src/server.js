import express from 'express';
import bodyParser from 'body-parser';
import {fromPairs, map} from 'lodash';

import eqn_typeset from './eqn-typeset';
import item_data_to_html from './item-data-to-html';
import markup_to_item_data from './markup-to-item-data';
import {ITEM_NAMES} from './constants';

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
    markup_to_item_data(req.body.body).then(result => {
        json_response(res, result);
    });
});

app.post('/render-eqns', function(req, res) {
    const typeset_jobs = map(req.body.eqns, (data, key) => eqn_typeset(key, data));
    return Promise.all(typeset_jobs).then(eqn_list => {
        json_response(res, fromPairs(eqn_list));
    }).catch(() => {
        json_response(res, {error: true});
    });
});

app.post('/render-item', function(req, res) {
    const item_type = req.body.item_type,
        document = req.body.document,
        eqns = req.body.eqns,
        concepts = req.body.concepts,
        refs = req.body.refs;
    if (item_type in ITEM_NAMES && document) {
        item_data_to_html(item_type, document, eqns, concepts, refs)
            .then(data => {
                json_response(res, data);
            });
    } else {
        res.status(400).send('Malformed data');
    }
});

app.listen(3000, function () {
  console.log('Listening on port 3000');
});
