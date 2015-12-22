import marked from 'marked';

marked.setOptions({
  sanitize: true,
});

var img_re = new RegExp('<img src="([^"]*)".*?>', 'g'),
    anchor_re = new RegExp('<a href="([^"]*)">(.*?)</a>', 'g'),
    con_def_re = new RegExp('^=([-0-9a-zA-Z_]+)$'),
    item_ref = new RegExp('^([^#]+)(?:#([-0-9a-zA-Z_]+))?$'),
    md_link_re = new RegExp('(?!!)\\[([^\\]]*)\\]\\(([^\)]*)\\)', 'g');

function normalizeTeX(tex) {
   return tex.trim().replace(/(\\[a-zA-Z]+) +([a-zA-Z])/g , '$1{\\\\}$2').replace(/ +/g, '').replace(/\{\\\\\}/g, ' ')
}

function prepareEquations(eqns) {
    var peqns = {};
    for (let key in eqns) {
        let eqn = eqns[key];
        peqns[key] = {
            html: '<script type="math/tex' + (eqn.block ? '; mode=display' : '') + '">' + eqn.source + '</script>',
            mathjax: true
        };
    }
    return peqns;
}

export function textToItemData(text) {
    var idToEqn = {}, eqnToId = {}, eqnCounter = 0,
        defined = {}, refs = {}, body;

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

    body = text.split(/\s*\$\$\s*/).map(function (para, j) {
        return (j % 2) ? '![](eqn/' + getEqnId(para, true) + ')' :
            para.split('$').map(function (item, k) {
                return (k % 2) ? '![](eqn/' + getEqnId(item, false) + ')'
                    : item.replace(md_link_re, function(all, text, link) {
                        var match = link.match(con_def_re);
                        if (match) {
                            defined[match[1]] = true;
                            return all;
                        }
                        match = link.match(item_ref);
                        if (match) {
                            refs[match[1]] = true;
                            return all;
                        }
                        return '\\[' + text + '\\]\\(' + link + '\\)';
                    });
            }).join('');
    }).join('\n\n');

    return {
        body: body,
        defined: Object.keys(defined),
        item_refs: Object.keys(refs),
        eqns: idToEqn
    };
}

export function itemDataToHtml(data) {
    var eqns = prepareEquations(data.eqns || {}),
        mathjax = false, html;

    html = marked(data.body);
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
    html = html.replace(anchor_re, function (_, ref, txt) {
        var match = ref.match(con_def_re);
        if (match) {
            ref = match[1];
            txt = txt || ref;
            return '<span class="defined" data-concept="' + ref + '">' + txt + '</span>';
        }
        match = ref.match(item_ref);
        if (match) {
            txt = txt || match[1];
            return '<a href="/item/' + ref + '">' + txt + '</a>';
        }
        return '<em>error</em>';
    });

    return {html: html, mathjax: mathjax};
}
