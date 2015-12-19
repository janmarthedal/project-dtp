import React from 'react';
import marked from 'marked';

marked.setOptions({
  sanitize: true,
});

var img_re = new RegExp('<img src="([^"]*)".*?>', 'g');

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

function dataItemToHtml(data) {
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

export default class extends React.Component {
    constructor(props) {
        super(props);
        this.state = props.data || {body: ''};
        this.updateMathJax = false;
    }
    setItemData(data) {
        this.setState(data);
    }
    componentDidMount() {
        this.postRender();
    }
    componentDidUpdate() {
        this.postRender();
    }
    postRender() {
        if (this.updateMathJax) {
            window.MathJax.Hub.Queue(['Typeset', MathJax.Hub, this.refs.viewer]);
            this.updateMathJax = false;
        }
    }
    render() {
        var output = dataItemToHtml(this.state);
        var markup = {__html: output.html};
        this.updateMathJax = output.mathjax;
        return (
            <div ref='viewer' className="item-view" dangerouslySetInnerHTML={markup} />
        );
    }
}
