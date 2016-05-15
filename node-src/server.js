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

function md_dom_to_item_dom(node) {
    if (node.nodeType === 1) {
        const item_node = {};
        const children = Array.prototype.map.call(node.childNodes, child => md_dom_to_item_dom(child));
        if (node.localName === 'img') {
            const src = node.getAttribute('src');
            if (src.startsWith('/eqn/')) {
                item_node.type = 'eqn';
                item_node.id = parseInt(src.substring(5));
            } else {
                console.error('Unknown img');
            }
        } else if (node.localName === 'a') {
            const href = node.getAttribute('href');
            if (href.startsWith('=')) {
                item_node.type = 'concept-def';
                item_node.tag = href.substring(1);
            } else {
                console.error('Unknown a');
            }
        } else {
            item_node.type = node.localName;
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
        console.error('Unknown node');
    }
}

function textToItemData(text, callback) {
    const idToEqn = {}, eqnToId = {},
        paragraphs = text.split(/\s*\$\$\s*/);
    let counter = 0;

    function getEqnId(tex, block) {
        tex = normalizeTeX(tex);
        let key = (block ? 'B' : 'I') + tex;
        if (key in eqnToId)
            return eqnToId[key];
        counter++;
        eqnToId[key] = counter;
        idToEqn[counter] = {block: block, source: tex};
        return counter;
    }

    if (paragraphs.length % 2 === 0)
        paragraphs.pop();

    let clean_text = paragraphs.map(function (para, j) {
        if (j % 2) {
            return '![](/eqn/' + getEqnId(para, true) + ')';
        } else {
            let items = para.split('$');
            if (items.length % 2 === 0)
                items.pop();
            return items.map(function (item, k) {
                if (k % 2) {
                    return '![](/eqn/' + getEqnId(item, false) + ')';
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
            body: item_dom.children,
            eqns: idToEqn
        });
    });
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

app.post('/typeset', function(req, res) {
    if (!req.body.eqns) {
        res.status(400).send('Malformed data')
        return;
    }
    Promise.all(req.body.eqns.map(function (item) {
        return typeset(item.id, item.math, item.format);
    })).then(function (results) {
        json_response(res, results);
    }, function (err) {
        res.status(500).send('Typeset error');
    });
});

function test_md() {
    var html = marked('I am using __markdown__.\n\n[foo](bar)\n\n<a href="#">link</a>');
    jsdom.env(html, function (err, window) {
        var body = window.document.body;
        var elems = body.getElementsByTagName('a');
        for (var i = 0; i < elems.length; i++) {
            var href = elems[i].getAttribute('href');
            if (href) {
                href = '=' + href;
                elems[i].setAttribute('href', href);
                console.log(href);
            }
        }
        console.log(body.outerHTML);
        window.close();
    });
}

//test_md();

var st = 'Let $x \\in \\mathbb{R}$ be a [real number](=real-number). Then\n\n$$\n\\sum_{k=1}^n k = \\frac{n(n+1)}{2}\n$$\n\nAnd the result follows.\n';
textToItemData(st, function (data) {
    console.log(JSON.stringify(data));
});

/*app.listen(3000, function () {
  console.log('Listening on port 3000');
});*/
