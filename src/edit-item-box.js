import React from 'react';

export default React.createClass({
    setValue: function (value) {
        this.textarea.value = value;
        this.props.onChange(value);
    },
    render: function () {
        return (
            <textarea onChange={(event) => this.props.onChange(event.target.value)}
                ref={(ref) => this.textarea=ref}
                className="edit-item-box pure-input-1" name="body"
                placeholder="Math item source" />
        );
    }
});
