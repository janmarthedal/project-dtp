import React from 'react';
import EditItemBox from './edit-item-box';
import RenderItemBox from './render-item-box';

export default React.createClass({
    componentDidMount: function () {
        if (this.props.value)
            this.editor.setValue(this.props.value);
    },
    render: function () {
        return (
            <form className="pure-form" method="post">
                <EditItemBox onChange={(value) => this.viewer.setBody(value)}
                    ref={(ref) => this.editor=ref} />
                <RenderItemBox ref={(ref) => this.viewer=ref} />
                <button type="submit" className="pure-button pure-button-primary">Create</button>
            </form>
        );
    }
});
