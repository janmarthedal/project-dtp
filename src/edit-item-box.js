import React from 'react';

export default class extends React.Component {
    constructor(props) {
        super(props);
        this.timer = null;
        this._onChange = this._onChange.bind(this);
    }
    setValue(value) {
        this.refs.textarea.value = value;
        this.props.onChange(value);
    }
    _onChange(event) {
        if (this.timer)
            window.clearTimeout(this.timer);
        this.timer = window.setTimeout(() => {
            this.timer = null;
            this.props.onChange(event.target.value);
        }, 500);
    }
    render() {
        return (
            <textarea onChange={this._onChange} name="body" ref='textarea'
                className="edit-item-box pure-input-1" placeholder="Math item source" />
        );
    }
}
