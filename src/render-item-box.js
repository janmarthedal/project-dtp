import React from 'react';
import marked from 'marked';

marked.setOptions({
  sanitize: true,
});

export default class extends React.Component {
    constructor(props) {
        super(props);
        this.state = {body: props.source || ''};
    }
    setBody(value) {
        this.setState({body: value});
    }
    render() {
        var markup = {__html: marked(this.state.body)};
        return (
            <div className="item-view" dangerouslySetInnerHTML={markup} />
        );
    }
}
