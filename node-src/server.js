'use strict';

const express = require('express');
const bodyParser = require('body-parser');
const mjAPI = require('mathjax-node/lib/mj-single.js');
const marked = require('marked');
const jsdom = require('jsdom');

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

const regex_tag_def = /^=[-a-z]+$/;

function make_error(reason) {
    return {
        type: 'error',
        reason: reason
    };
}

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
                return make_error("illegal img source '" + src + "'");
            }
        } else if (node.localName === 'a') {
            const href = node.getAttribute('href') || '';
            if (regex_tag_def.test(href)) {
                item_node.type = 'tag-def';
                item_node.tag = href.substring(1);
            } else if (href.startsWith('=')) {
                return make_error("illegal tag '" + tag + "'");
            } else {
                return make_error("illegal item reference '" + href + "'");
            }
        } else if (node.localName in tag_map) {
            item_node.type = tag_map[node.localName];
        } else {
            return make_error('unsupported HTML tag ' + node.localName);
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
        return make_error('unsupported HTML node type ' + node.nodeValue);
    }
}

class EqnMap {
    constructor() {
        this.counter = 0;
        this.eqns = {};
        this.eqnToId = {};
    }
    get_id(tex, block) {
        tex = normalizeTeX(tex);
        const key = (block ? 'B' : 'I') + tex;
        if (key in this.eqnToId)
            return this.eqnToId[key];
        const id = ++this.counter;
        this.eqnToId[key] = id;
        this.eqns[id] = {
            format: block ? 'TeX' : 'inline-TeX',
            math: tex
        };
        return id;
    }
    get_eqn_map() {
        return this.eqns;
    }
}

function prepare_markdown(text) {
    const eqn_map = new EqnMap(),
        paragraphs = text.split(/\s*\$\$\s*/);

    if (paragraphs.length % 2 === 0)
        paragraphs.pop();

    const clean_text = paragraphs.map(function (para, j) {
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

    return Promise.resolve({
        text: clean_text,
        eqns: eqn_map.get_eqn_map()
    });
}

function markdownify(text) {
    return Promise.resolve(marked(text));
}

function html_to_item_dom(html) {
    return new Promise(function (resolve, reject) {
        jsdom.env(html, function (err, window) {
            if (!err) {
                const body = window.document.body;
                const item_dom = md_dom_to_item_dom(body);
                window.close();
                resolve(item_dom);
            } else {
                reject(err);
            }
        });
    });
}

function markdown_to_item_dom(text) {
    return prepare_markdown(text).then(prepared => {
        return Promise.all([
            markdownify(prepared.text),
            prepared.eqns
        ]);
    }).then(values => {
        return Promise.all([
            html_to_item_dom(values[0]),
            values[1]
        ]);
    }).then(values => {
        return {
            document: values[0],
            eqns: values[1]
        }
    });
}

function item_node_to_html(node, eqns) {
    if (node.type === 'text')
        return node.value;
    if (node.type === 'eqn') {
        const item = eqns[node.id];
        if (item.error)
            return '<span class="text-danger">' + item.error + '</span>';
        else
            return item.html;
    }
    if (node.type === 'error')
        return '<span class="text-danger">' + node.reason + '</span>';
    let children = (node.children || []).map(child => item_node_to_html(child, eqns));
    children = children.join('');
    if (node.type === 'body')
        return children;
    if (node.type === 'para')
        return '<p>' + children + '</p>';
    if (node.type === 'tag-def')
        return '<em>' + children + '</em>';
    return '<span class="text-danger">unsupported node type \'' + node.type + "'";
}

function item_dom_to_html(root, eqns) {
    return Promise.resolve(item_node_to_html(root, eqns || {}));
}

/* */

function typeset(id, data) {
    if (['TeX', 'inline-TeX'].indexOf(data.format) < 0)
        return Promise.reject('illegal typeset format');
    return new Promise(function (resolve, reject) {
        console.log('Typesetting: ' + data.math);
        mjAPI.typeset({
            math: data.math,
            format: data.format,
            html: true,
        }, function (result) {
            if (result.errors) {
                resolve([id, { error: result.errors }]);
            } else {
                resolve([id, { html: result.html }]);
            }
        });
    });
}

function json_response(res, data) {
    res.setHeader('Content-Type', 'application/json');
    res.send(JSON.stringify(data));
}

function object_to_array(obj) {
    const result = [];
    for (const key in obj)
        result.push([key, obj[key]]);
    return result;
}

function array_to_object(list) {
    const result = {};
    list.forEach(item => {
        result[item[0]] = item[1];
    });
    return result;
}

var app = express();

app.use(bodyParser.json());

app.get('/', function (req, res) {
    json_response(res, {'ok': true});
});

app.post('/prepare-item', function(req, res) {
    if (req.body.text) {
        markdown_to_item_dom(req.body.text).then(data => {
            const promise_list = object_to_array(data.eqns || {})
                .map(item => typeset(item[0], item[1]));
            promise_list.push(data.document);
            return Promise.all(promise_list);
        }).then(values => {
            const document = values.pop();
            const eqns = array_to_object(values);
            json_response(res, {
                document: document,
                eqns: eqns
            });
        });
    } else {
        res.status(400).send('Malformed data')
    }
});

app.post('/render-item', function(req, res) {
    if (req.body.document) {
        item_dom_to_html(req.body.document, req.body.eqns).then(html => {
            json_response(res, {html: html});
        });
    } else {
        res.status(400).send('Malformed data');
    }
});

app.listen(3000, function () {
  console.log('Listening on port 3000');
});
