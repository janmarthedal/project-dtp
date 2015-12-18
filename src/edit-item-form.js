import React from 'react';
import EditItemBox from './edit-item-box';
import RenderItemBox from './render-item-box';

export default React.createClass({
    render: function() {
        return (
            <form className="pure-form" method="post">
                <EditItemBox />
                <RenderItemBox />
                <button type="submit" className="pure-button pure-button-primary">Create</button>
            </form>
        );
    }
});
