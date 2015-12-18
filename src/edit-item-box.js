import React from 'react';

export default React.createClass({
    setValue: function (value) {
        this.refs.textarea.value = value;
        this.props.onChange(value);
    },
    render: function () {
        return (
            <textarea onChange={(event) => this.props.onChange(event.target.value)}
                className="edit-item-box pure-input-1" name="body"
                ref='textarea' placeholder="Math item source" />
        );
    }
});
