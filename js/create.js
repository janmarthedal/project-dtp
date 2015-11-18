(function (window, undefined) {
    let $ = window.jQuery,
        input = $('#input'),
        preview = $('#preview'),
        timerId,
        img_re = new RegExp('<img src="([^"]*)".*?>', 'g'),
        anchor_re = new RegExp('<a href="([^"]*)">(.*?)</a>', 'g'),
        slug_re = new RegExp('^[-0-9a-zA-Z_]+$');

    class EqnManager {
        constructor() {
            this.eqnCache = {};
            this.eqnIds = {};
            this.eqnCounter = 0;
        }
        getId(tex, block_mode) {
            tex = normalizeTeX(tex);
            let key = (block_mode ? 'B' : 'I') + tex;
            let id = this.eqnCache[key];
            if (!id) {
                id = this.eqnCache[key] = ++this.eqnCounter;
                this.eqnIds[id] = '<script type="math/tex' + (block_mode ? '; mode=display' : '') + '">' + tex + '</script>';
            }
            return id;
        }
        toHtml(id) {
            return this.eqnIds[id];
        }
    }

    function normalizeTeX(tex) {
        return tex.trim().replace(/(\\[a-zA-Z]+) +([a-zA-Z])/g , '$1{\\\\}$2').replace(/ +/g, '').replace(/\{\\\\\}/g, ' ')
    }

    function updatePreview() {
        let text = input.val(),
            eqns = new EqnManager();

        timerId = undefined;
        text = text.split(/\s*\$\$\s*/).map(function (p, j) {
            return (j % 2) ? '![](eqn/' + eqns.getId(p, true) + ')' :
                p.split('$').map(function (t, k) {
                    return (k % 2) ? '![](eqn/' + eqns.getId(t, false) + ')' : t;
                }).join('');
        }).join('\n\n');

        let html = window.marked(text, {sanitize: true});
        html = html.replace(img_re, function (_, m) {
            var h;
            if (m.indexOf('eqn/') == 0)
                h = eqns.toHtml(m.substring(4));
            return h || '<em>error</em>';
        });
        html = html.replace(anchor_re, function (_, ref, txt) {
            var h;
            if (ref.indexOf('=') == 0 && ref.length > 1 && ref.substring(1).search(slug_re) === 0) {
                ref = ref.substring(1);
                txt = txt || ref;
                h = '<span class="defined" data-concept="' + ref + '">' + txt + '</span>';
            }
            return h || '<em>error</em>';
        });

        preview.html(html);
        //preview.text(html);

        window.MathJax.Hub.Queue(['Typeset', MathJax.Hub, 'preview']);
    }

    input.on('input propertychange', function () {
        if (timerId) window.clearTimeout(timerId);
        timerId = window.setTimeout(updatePreview, 200);
    });

    input.focus();

})(window);
