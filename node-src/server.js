'use strict';

var express = require('express');
var bodyParser = require('body-parser');
var mjAPI = require('mathjax-node/lib/mj-single.js');
var marked = require('marked');
var jsdom = require('jsdom');

// Initialize marked
marked.setOptions({
  gfm: false,
  pedantic: false,
  sanitize: true,
});

// Initialize mathjax-node
mjAPI.config({MathJax: {}});
mjAPI.start();

/* Pure functions */

function normalizeTeX(tex) {
   return tex.trim().replace(/(\\[a-zA-Z]+) +([a-zA-Z])/g , '$1{\\\\}$2').replace(/ +/g, '').replace(/\{\\\\\}/g, ' ')
}

const tag_map = {
    'body': 'body',
    'p': 'para',
};

function md_dom_to_item_dom(node) {
    if (node.nodeType === 1) {
        const item_node = {};
        const children = Array.prototype.map.call(node.childNodes, child => md_dom_to_item_dom(child));
        if (node.localName === 'img') {
            const src = node.getAttribute('src') || '';
            if (src.startsWith('/eqn/')) {
                return {
                    type: 'eqn',
                    id: parseInt(src.substring(5))
                }
            } else {
                return {
                    type: 'error',
                    reason: "Illegal img source '" + src + "'",
                }
            }
        } else if (node.localName === 'a') {
            const href = node.getAttribute('href') || '';
            if (href.startsWith('=')) {
                item_node.type = 'tag-def';
                item_node.tag = href.substring(1);
            } else {
                return {
                    type: 'error',
                    reason: "Illegal a href '" + href + "'",
                }
            }
        } else if (node.localName in tag_map) {
            item_node.type = tag_map[node.localName];
        } else {
            return {
                type: 'error',
                reason: 'Unsupported HTML tag ' + node.localName,
            }
        }
        if (children.length)
            item_node.children = children
        return item_node;
    } else if (node.nodeType === 3) {
        return {
            type: 'text',
            value: node.nodeValue
        }
    } else {
        return {
            type: 'error',
            reason: 'Unsupported HTML node type ' + node.nodeValue
        }
    }
}

class EqnMap {
    constructor() {
        this.counter = 0;
        this.eqns = [];
        this.eqnToId = {};
    }
    get_id(tex, block) {
        tex = normalizeTeX(tex);
        let key = (block ? 'B' : 'I') + tex;
        if (key in this.eqnToId)
            return this.eqnToId[key];
        this.counter++;
        this.eqnToId[key] = this.counter;
        this.eqns.push({
            id: this.counter,
            format: block ? 'TeX' : 'inline-TeX',
            math: tex,
        });
        return this.counter;
    }
    get_eqn_list() {
        return this.eqns;
    }
}

function textToItemData(text, callback) {
    const eqn_map = new EqnMap(),
        paragraphs = text.split(/\s*\$\$\s*/);

    if (paragraphs.length % 2 === 0)
        paragraphs.pop();

    let clean_text = paragraphs.map(function (para, j) {
        if (j % 2) {
            return '![](/eqn/' + eqn_map.get_id(para, true) + ')';
        } else {
            let items = para.split('$');
            if (items.length % 2 === 0)
                items.pop();
            return items.map(function (item, k) {
                if (k % 2) {
                    return '![](/eqn/' + eqn_map.get_id(item, false) + ')';
                } else {
                    return item;
                }
            }).join('');
        }
    }).join('\n\n');

    let html = marked(clean_text);
    console.log(html);
    jsdom.env(html, function (err, window) {
        const body = window.document.body;
        const item_dom = md_dom_to_item_dom(body);
        callback({
            document: item_dom,
            eqns: eqn_map.get_eqn_list()
        });
        window.close();
    });
}

function item_node_to_html(node) {
    if (node.type === 'text')
        return node.value;
    if (node.type === 'eqn')
        return '[EQN ' + node.id + ']';
    let children = (node.children || []).map(item_dom_to_html);
    children = children.join('');
    if (node.type === 'body')
        return children;
    if (node.type === 'para')
        return '<p>' + children + '</p>';
    if (node.type === 'tag-def')
        return '<em>' + children + '</em>';
    return '???';
}

function item_dom_to_html(root, eqns) {
    return item_node_to_html(root);
}

/* */

function typeset(id, math, format) {
    if (['TeX', 'inline-TeX'].indexOf(format) < 0)
        return Promise.reject('illegal typeset format');
    return new Promise(function (resolve, reject) {
        console.log('Typesetting: ' + math);
        mjAPI.typeset({
            math: math,
            format: format,
            html: true,
        }, function (data) {
            if (data.errors) {
                reject(data.errors);
            } else {
                resolve({
                    id: id,
                    html: data.html
                });
            }
        });
    });
}

function json_response(res, data) {
    res.setHeader('Content-Type', 'application/json');
    res.send(JSON.stringify(data));
}

var app = express();

app.use(bodyParser.json());

app.get('/', function (req, res) {
    json_response(res, {'ok': true});
});

app.post('/typeset-eqns', function(req, res) {
    if (!req.body.eqns) {
        res.status(400).send('Malformed data')
        return;
    }
    Promise.all(req.body.eqns.map(function (item) {
        return typeset(item.id, item.math, item.format);
    })).then(function (results) {
        json_response(res, results);
    }, function (err) {
        console.error('Typeset error ' + err);
        res.status(500).send('Typeset error ' + err);
    });
});

app.post('/prep-md-item', function(req, res) {
    if (!req.body.text) {
        res.status(400).send('Malformed data')
        return;
    }
    textToItemData(req.body.text, function (data) {
        console.log(item_dom_to_html(data.document));
        json_response(res, data);
    });
});

app.post('/typeset-item', function(req, res) {
    if (!req.body.document) {
        res.status(400).send('Malformed data')
        return;
    }
    let html = item_dom_to_html(req.body.document);
    json_response(res, {html: html});
});

app.listen(3000, function () {
  console.log('Listening on port 3000');
});
