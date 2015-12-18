import React from 'react';

export default React.createClass({
    getInitialState: function() {
        return {body: this.props.source || ''};
    },
    setBody: function(value) {
        this.setState({body: value});
    },
    render: function() {
        return (
            <div className="item-view">{this.state.body}</div>
        );
    }
});
