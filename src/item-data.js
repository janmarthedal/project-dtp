import marked from 'marked';

marked.setOptions({
  sanitize: true,
});

const img_re = new RegExp('<img src="([^"]*)".*?>', 'g'),
    anchor_re = new RegExp('<a href="([^"]*)">(.*?)</a>', 'g'),
    con_def_re = new RegExp('^=([-0-9a-zA-Z_]+)$'),
    con_ref_re = new RegExp('^#([-0-9a-zA-Z_]+)$'),
    item_ref_re = new RegExp('^([^#]+)(?:#([-0-9a-zA-Z_]+))?$'),
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
    const idToEqn = {}, eqnToId = {}, conceptToId = {}, idToConcept = {},
        itemRefToId = {}, idToItemRef = {}, con_refs = {}, con_defs = {},
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

    function lookupId(st, stToId, idToSt) {
        if (st in stToId)
            return stToId[st];
        counter++;
        stToId[st] = counter;
        idToSt[counter] = st;
        return counter;
    }

    function getConDefId(con) {
        const id = lookupId(con, conceptToId, idToConcept);
        con_defs[id] = true;
        return id;
    }

    function getConRefId(con) {
        const id = lookupId(con, conceptToId, idToConcept);
        con_refs[id] = true;
        return id;
    }

    function getItemRefId(ref) {
        return lookupId(ref, itemRefToId, idToItemRef);
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
                        if (match)
                            return '[' + text + '](=' + getConDefId(match[1]) + ')';
                        match = link.match(con_ref_re);
                        if (match)
                            return '[' + text + '](#' + getConRefId(match[1]) + ')';
                        match = link.match(item_ref_re);
                        if (match)
                             return '[' + text + '](' + getItemRefId(match[1]) + ')';
                        return '\\[' + text + '\\]\\(' + link + '\\)';
                    });
            }).join('');
        }
    }).join('\n\n');

    return {
        body: body,
        concept_map: idToConcept,
        concept_defs: Object.keys(con_defs),
        concept_refs: Object.keys(con_refs),
        item_refs: idToItemRef,
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
            ref = data.concept_map[match[1]];
            txt = txt || ref;
            return '<span class="defined" data-concept="' + ref + '">' + txt + '</span>';
        }
        match = ref.match(con_ref_re);
        if (match) {
            ref = data.concept_map[match[1]];
            txt = txt || ref;
            return '<a href="/concept/' + ref + '">' + txt + '</a>';
        }
        match = ref.match(item_ref_re);
        if (match) {
            ref = data.item_refs[match[1]];
            txt = txt || ref;
            return '<a href="/items/' + ref + '">' + txt + '</a>';
        }
        return '<em>error</em>';
    });

    return {html, mathjax};
}
