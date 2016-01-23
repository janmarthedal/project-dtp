import React from 'react';
import {itemDataToHtml} from './item-data';

export default class extends React.Component {
    constructor(props) {
        super(props);
    }
    render() {
        const output = itemDataToHtml(this.props.data),
            markup = {__html: output.html},
            classes = ['item-view'];
        if (output.mathjax)
            classes.push('mj-typeset');
        return (
            <div className={classes.join(' ')} dangerouslySetInnerHTML={markup} />
        );
    }
}
