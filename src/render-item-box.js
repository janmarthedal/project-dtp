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
        var output = itemDataToHtml(this.state);
        var markup = {__html: output.html};
        this.updateMathJax = output.mathjax;
        return (
            <div ref='viewer' className="item-view" dangerouslySetInnerHTML={markup} />
        );
    }
}
