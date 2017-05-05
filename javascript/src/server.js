import express from 'express';
import bodyParser from 'body-parser';
import {fromPairs, map} from 'lodash';

import eqn_typeset from './eqn-typeset';
import item_data_to_html from './item-data-to-html';
import markup_to_item_data from './markup-to-item-data';
import {ITEM_NAMES} from './constants';
import parse_cindy from './parse-cindy';


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
        refs = req.body.refs,
        media = req.body.media;
    if (item_type in ITEM_NAMES && document) {
        item_data_to_html(item_type, document, eqns, concepts, refs, media)
            .then(data => {
                json_response(res, data);
            });
    } else {
        res.status(400).send('Malformed data');
    }
});

app.post('/parse-cindy', function(req, res) {
    parse_cindy(req.body.html_file)
        .then(result => {
            json_response(res, result);
        })
        .catch(err => {
            json_response(res, {error: 'Unable to read file'});
        });
});

app.listen(3000, function () {
  console.log('Listening on port 3000');
});

/*import fs from 'fs';

const cindy_file = fs.readFileSync('/Users/jmr/projects/geometry-images/cinderella/html/thales-theorem.html');

const data = parse_cindy(cindy_file);
    
//const data = parse_cindy('<!DOCTYPE html><html><head><title>thales-theorem.cdy</title><script type="text/javascript" src="http://cinderella.de/CindyJS/latest/Cindy.js"></script><script type="text/javascript">\ncreateCindy({\nscripts: "cs*"});</script></head><body></body></html>');

console.log(JSON.stringify(data));
*/