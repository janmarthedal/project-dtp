
function cleanElement(el) {
    el.removeAttribute('id');
    el.removeAttribute('role');
    el.removeAttribute('tabindex');
}

export default class CHtmlCache {
    constructor() {
        this._cache = [];
        this._newElements = [];
        teoremer.MathJaxReady.then(MathJax => {
            console.log('MathJax ready');
            MathJax.Hub.Register.MessageHook('New Math', message => {
                var script = MathJax.Hub.getJaxFor(message[1]).SourceElement();
                this._newElements.push(script);
            });
            MathJax.Hub.Register.MessageHook('End Process', () => {
                this._processElements();
            });
        });
    }
    _processElements() {
        this._newElements.forEach(script => {
            let html = script.previousSibling.cloneNode(true),
                block = script.getAttribute('type') !== 'math/tex';
            cleanElement(html);
            Array.prototype.forEach.call(html.querySelectorAll('*'), cleanElement);
            this._add(script.text, block, html.outerHTML);
        });
        this._newElements = [];
    }
    _find_index(tex, block) {
        var k, item;
        for (k=0; k < this._cache.length; k++) {
            item = this._cache[k];
            if (block === item.block && tex === item.tex)
                return k;
        }
        return -1;
    }
    _add(tex, block, html) {
        //console.log('CHtmlCache._add', block, tex);
        if (this.get_html(tex, block))
            return;
        if (this._cache.length >= CHtmlCache.CACHE_SIZE)
            this._cache.pop();
        this._cache.unshift({tex, block, html});
    }
    debug() {
        return this._cache;
    }
    get_html(tex, block) {
        var index = this._find_index(tex, block), item;
        //console.log('get_html', block, tex, index, this._cache);
        if (index < 0)
            return null;
        item = this._cache.splice(index, 1)[0];
        this._cache.unshift(item);
        return item.html;
    }
}

CHtmlCache.CACHE_SIZE = 100;
