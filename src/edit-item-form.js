import React from 'react';
import EditItemBox from './edit-item-box';
import RenderItemBox from './render-item-box';
import {textToItemData} from './item-data';

export default class extends React.Component {
    constructor(props) {
        super(props);
        this.state = {body: this.props.body || ''};
        this.onChange = this.onChange.bind(this);
    }
    onChange(text) {
        this.setState({body: text});
    }
    render() {
        const body = this.state.body,
            data = textToItemData(body);
        return (
            <form className="pure-form" method="post">
                <EditItemBox initialBody={body} onChange={this.onChange} />
                <RenderItemBox data={data} mathjax_ready={this.props.mathjax_ready} chtml_cache={this.props.chtml_cache} />
                <button type="submit" className="pure-button pure-button-primary">Save</button>
            </form>
        );
    }
}
