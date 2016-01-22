import React from 'react';

export default class extends React.Component {
    constructor(props) {
        super(props);
        this.timer = null;
        this._onChange = this._onChange.bind(this);
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
            <textarea onChange={this._onChange} name="body"
                className="edit-item-box pure-input-1" placeholder="Math item source"
                defaultValue={this.props.initialBody} />
        );
    }
}
