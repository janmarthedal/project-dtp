import React from 'react';
import marked from 'marked';

marked.setOptions({
  sanitize: true,
});

export default React.createClass({
    getInitialState: function() {
        return {body: this.props.source || ''};
    },
    setBody: function(value) {
        this.setState({body: value});
    },
    render: function() {
        var markup = {__html: marked(this.state.body)};
        return (
            <div className="item-view" dangerouslySetInnerHTML={markup} />
        );
    }
});
