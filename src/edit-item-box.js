import React from 'react';

export default React.createClass({
    onChange: function (ev) {
        console.log('change');
    },

    render: function() {
        return (
            <textarea onChange={this.onChange} className="edit-item-box pure-input-1" name="body" placeholder="Math item source"></textarea>
        );
    }
});
