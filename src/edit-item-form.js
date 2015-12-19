import React from 'react';
import EditItemBox from './edit-item-box';
import RenderItemBox from './render-item-box';

export default class extends React.Component {
    setBody(value) {
        this.refs.editor.setValue(value);
    }
    render() {
        return (
            <form className="pure-form" method="post">
                <EditItemBox ref='editor'
                    onChange={(value) => this.refs.viewer.setBody(value)} />
                <RenderItemBox ref='viewer' />
                <button type="submit" className="pure-button pure-button-primary">Create</button>
            </form>
        );
    }
}
