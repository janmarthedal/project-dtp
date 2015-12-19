import marked from 'marked';

marked.setOptions({
  sanitize: true,
});

var img_re = new RegExp('<img src="([^"]*)".*?>', 'g');

function normalizeTeX(tex) {
   return tex.trim().replace(/(\\[a-zA-Z]+) +([a-zA-Z])/g , '$1{\\\\}$2').replace(/ +/g, '').replace(/\{\\\\\}/g, ' ')
}

function prepareEquations(eqns) {
    var peqns = {};
    for (let key in eqns) {
        let eqn = eqns[key];
        peqns[key] = {
            html: '<script type="math/tex' + (eqn.block ? '; mode=display' : '') +
                '">' + eqn.source + '</script>',
            mathjax: true
        };
    }
    return peqns;
}

export function itemDataToHtml(data) {
    var eqns = prepareEquations(data.eqns || {}),
        html = marked(data.body),
        mathjax = false;
    html = html.replace(img_re, function (_, m) {
        if (m.indexOf('eqn/') == 0) {
            let eqn = eqns[m.substring(4)];
            if (eqn) {
                mathjax = mathjax || eqn.mathjax;
                return eqn.html;
            }
        }
        return '<em>error</em>';
    });
    return {html: html, mathjax: mathjax};
}

export function textToItemData(text) {
    var idToEqn = {}, eqnToId = {}, eqnCounter = 0, body;

    function getEqnId(tex, block) {
        tex = normalizeTeX(tex);
        let key = (block ? 'B' : 'I') + tex;
        if (key in eqnToId)
            return eqnToId[key];
        eqnCounter++;
        eqnToId[key] = eqnCounter;
        idToEqn[eqnCounter] = {block: block, source: tex};
        return eqnCounter;
    }

    body = text.split(/\s*\$\$\s*/).map(function (p, j) {
        return (j % 2) ? '![](eqn/' + getEqnId(p, true) + ')' :
            p.split('$').map(function (t, k) {
                return (k % 2) ? '![](eqn/' + getEqnId(t, false) + ')' : t;
            }).join('');
    }).join('\n\n');

    return {
        body: body,
        eqns: idToEqn
    };
}
