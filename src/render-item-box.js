import React from 'react';
import {itemDataToHtml} from './item-data';

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
        const output = itemDataToHtml(this.state, this.props.chtml_cache),
            markup = {__html: output.html};
        this.updateMathJax = output.mathjax;  // save for postRender
        return (
            <div ref='viewer' className="item-view" dangerouslySetInnerHTML={markup} />
        );
    }
}
