import React from 'react';
import RenderItemBox from './render-item-box';
import {textToItemData} from './item-data';

export default class extends React.Component {
    constructor(props) {
        super(props);
        this.state = {body: this.props.body || ''};
        this.timer = null;
        this.onChange = this.onChange.bind(this);
    }
    onChange(event) {
        if (this.timer)
            window.clearTimeout(this.timer);
        this.timer = window.setTimeout(() => {
            this.timer = null;
            this.setState({body: event.target.value});
        }, 500);
    }
    render() {
        const body = this.state.body, data = textToItemData(body);
        return (
            <form className="pure-form pure-form-stacked" method="post">
                <label htmlFor="edit-notes">Notes</label>
                <textarea id="edit-notes" name="notes" className="edit-notes-box pure-input-1"
                    defaultValue={this.props.notes} />
                <label htmlFor="edit-item">Math item source</label>
                <textarea id="edit-item" onChange={this.onChange} name="body"
                    className="edit-item-box pure-input-1" defaultValue={this.props.body} />
                <label>Preview</label>
                <RenderItemBox data={data} mathjax_ready={this.props.mathjax_ready} chtml_cache={this.props.chtml_cache} />
                <button type="submit" className="pure-button pure-button-primary">Save</button>
                <a href={this.props.linkCancel} className="pure-button button-danger pull-right">Cancel</a>
            </form>
        );
    }
}
