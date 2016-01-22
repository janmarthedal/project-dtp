import React from 'react';
import {itemDataToHtml} from './item-data';

export default class extends React.Component {
    constructor(props) {
        super(props);
        this.updateMathJax = false;
    }
    componentDidMount() {
        this.postRender();
    }
    componentDidUpdate() {
        this.postRender();
    }
    postRender() {
        // not called on server
        if (this.updateMathJax) {
            this.props.mathjax_ready.then(MathJax => {
                MathJax.Hub.Queue(['Typeset', MathJax.Hub, this.refs.viewer]);
                this.updateMathJax = false;
            });
        }
    }
    render() {
        const output = itemDataToHtml(this.props.data, this.props.chtml_cache),
            markup = {__html: output.html};
        this.updateMathJax = output.mathjax;  // save for postRender
        return (
            <div ref='viewer' className="item-view" dangerouslySetInnerHTML={markup} />
        );
    }
}
