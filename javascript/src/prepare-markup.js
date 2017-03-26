import {normalizeTeX, TeX_brace_balance} from './pure-fun';

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

export default function prepare_markup(text) {
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
            const result = [];

            for (let k = 0; k < items.length; k++) {
                let item = items[k];
                if (k % 2) {
                    while (k + 2 < items.length && TeX_brace_balance(item) > 0) {
                        item = [item, items[k + 1], items[k + 2]].join('$');
                        k += 2;
                    }
                    const id = k + 1 === items.length
                        ? eqn_map.get_error_id('unterminated inline equation')
                        : eqn_map.get_id(item, false);
                    result.push('![](/eqn/', id, ')');
                } else {
                    result.push(item);
                }
            }

            return result.join('');
        }
    }).join('\n\n');

    return {
        text: prepared_text,
        eqns: eqn_map.get_eqn_map()
    };
}
