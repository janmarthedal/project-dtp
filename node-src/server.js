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
    'strong': 'strong',
    'em': 'emph',
    'li': 'list-item',
};

const regex_tag_def = /^=[-a-z]+$/;
const regex_html_header = /^h([1-6])$/;

function make_error(reason) {
    return {type: 'error', reason: reason};
}

function md_dom_to_item_dom(node) {
    let match;
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
        } else if (node.localName === 'ul' || node.localName === 'ol') {
            item_node.type = 'list';
            item_node.ordered = node.localName === 'ol';
        } else if (!!(match = node.localName.match(regex_html_header))) {
            item_node.type = 'header';
            item_node.level = parseInt(match[1]);
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
    get_error_id(msg) {
        const id = ++this.counter;
        this.eqns[id] = {
            error: msg
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

    const prepared_text = paragraphs.map(function (para, j) {
        if (j % 2) {
            const id = (j === paragraphs.length - 1)
                ? eqn_map.get_error_id('unterminated block equation')
                : eqn_map.get_id(para, true);
            return '![](/eqn/' + id + ')';
        } else {
            const items = para.split('$');
            return items.map(function (item, k) {
                if (k % 2) {
                    const id = (k === items.length - 1)
                        ? eqn_map.get_error_id('unterminated inline equation')
                        : eqn_map.get_id(item, false);
                    return '![](/eqn/' + id + ')';
                } else {
                    return item;
                }
            }).join('');
        }
    }).join('\n\n');

    return Promise.resolve({
        text: prepared_text,
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
    return prepare_markdown(text)
        .then(prepared =>
            markdownify(prepared.text)
                .then(html => html_to_item_dom(html))
                .then(item_dom => ({
                    document: item_dom,
                    eqns: prepared.eqns
                }))
        );
}

function item_node_to_html(node, eqns) {
    if (node.type === 'text')
        return node.value;
    if (node.type === 'eqn') {
        const item = eqns[node.id];
        if (!item)
            item = {error: 'corrupt eqn reference'};
        if (item.error)
            return '<span class="text-danger">' + item.error + '</span>';
        return item.html;
    }
    if (node.type === 'error')
        return '<span class="text-danger">' + node.reason + '</span>';
    const children = (node.children || [])
        .map(child => item_node_to_html(child, eqns))
        .join('');
    if (node.type === 'body')
        return children;
    if (node.type === 'para')
        return '<p>' + children + '</p>';
    if (node.type === 'strong')
        return '<strong>' + children + '</strong>';
    if (node.type === 'emph')
        return '<em>' + children + '</em>';
    if (node.type === 'tag-def')
        return '<a href="#">' + children + '</a>';
    if (node.type === 'list')
        return node.ordered ? '<ol>' + children + '</ol>' : '<ul>' + children + '</ul>';
    if (node.type === 'list-item')
        return '<li>' + children + '</li>';
    if (node.type === 'header') {
        const tag = 'h' + node.level;
        return '<' + tag + '>' + children + '</' + tag + '>';
    }
    return '<span class="text-danger">unsupported node type \'' + node.type + "'";
}

function item_dom_to_html(root, eqns) {
    return Promise.resolve(item_node_to_html(root, eqns || {}));
}

/* */

function typeset(id, data) {
    if (data.error)
        return Promise.resolve([id, data]);
    if (['TeX', 'inline-TeX'].indexOf(data.format) < 0)
        return Promise.reject('illegal typeset format');
    return new Promise((resolve, reject) => {
        mjAPI.typeset({
            math: data.math,
            format: data.format,
            html: true,
        }, result => {
            resolve([id, result.errors ? {error: result.errors} : {html: result.html}]);
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
        markdown_to_item_dom(req.body.text).then(item_dom => {
            const typeset_jobs = object_to_array(item_dom.eqns || {})
                .map(item => typeset(item[0], item[1]));
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
