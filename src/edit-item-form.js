import React from 'react';
import EditItemBox from './edit-item-box';
import RenderItemBox from './render-item-box';

function normalizeTeX(tex) {
   return tex.trim().replace(/(\\[a-zA-Z]+) +([a-zA-Z])/g , '$1{\\\\}$2').replace(/ +/g, '').replace(/\{\\\\\}/g, ' ')
}

function processItemText(text) {
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

export default class extends React.Component {
    constructor(props) {
        super(props);
        this.onChange = this.onChange.bind(this);
    }
    setBody(value) {
        this.refs.editor.setValue(value);
    }
    onChange(text) {
        var data = processItemText(text);
        this.refs.viewer.setItemData(data);
    }
    render() {
        return (
            <form className="pure-form" method="post">
                <EditItemBox ref='editor' onChange={this.onChange} />
                <RenderItemBox ref='viewer' />
                <button type="submit" className="pure-button pure-button-primary">Create</button>
            </form>
        );
    }
}
