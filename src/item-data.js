import marked from 'marked';

marked.setOptions({
  sanitize: true,
});

const img_re = new RegExp('<img src="([^"]*)".*?>', 'g'),
    anchor_re = new RegExp('<a href="([^"]*)">(.*?)</a>', 'g'),
    con_def_re = new RegExp('^=([-0-9a-zA-Z_]+)$'),
    item_ref = new RegExp('^([^#]+)(?:#([-0-9a-zA-Z_]+))?$'),
    md_link_re = new RegExp('(?!!)\\[([^\\]]*)\\]\\(([^\)]*)\\)', 'g');

function normalizeTeX(tex) {
   return tex.trim().replace(/(\\[a-zA-Z]+) +([a-zA-Z])/g , '$1{\\\\}$2').replace(/ +/g, '').replace(/\{\\\\\}/g, ' ')
}

function prepareEquation(eqn, chtml_cache) {
    if (chtml_cache) {
        const html = chtml_cache.get_html(eqn.source, eqn.block);
        if (html)
            return {html: html};
    }
    return {
        html: '<script type="math/tex' + (eqn.block ? '; mode=display' : '') + '">' + eqn.source + '</script>',
        mathjax: true
    };
}

function prepareEquations(eqns, chtml_cache) {
    const peqns = {};
    for (let key in eqns)
        peqns[key] = prepareEquation(eqns[key], chtml_cache);
    return peqns;
}

export function textToItemData(text) {
    const idToEqn = {}, eqnToId = {}, defined = {}, refs = {},
       paragraphs = text.split(/\s*\$\$\s*/);
    let eqnCounter = 0;

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

    if (paragraphs.length % 2 === 0)
        paragraphs.pop();
    let body = paragraphs.map(function (para, j) {
        if (j % 2) {
            return '![](eqn/' + getEqnId(para, true) + ')';
        } else {
            let items = para.split('$');
            if (items.length % 2 === 0)
                items.pop();
            return items.map(function (item, k) {
                return (k % 2) ? '![](eqn/' + getEqnId(item, false) + ')'
                    : item.replace(md_link_re, function(all, text, link) {
                        let match = link.match(con_def_re);
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
        }
    }).join('\n\n');

    return {
        body: body,
        defined: Object.keys(defined),
        item_refs: Object.keys(refs),
        eqns: idToEqn
    };
}

export function itemDataToHtml(data, chtml_cache) {
    const eqns = prepareEquations(data.eqns || {}, chtml_cache);
    let mathjax = false,
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
        let match = ref.match(con_def_re);
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

    return {html, mathjax};
}
