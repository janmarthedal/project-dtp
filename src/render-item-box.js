import React from 'react';

export default class extends React.Component {
    constructor(props) {
        super(props);
        this.state = props.html || {html: ''};
    }
    componentDidMount() {
        this.postRender();
    }
    componentDidUpdate() {
        this.postRender();
    }
    postRender() {
        if (this.props.postRender)
            this.props.postRender();
    }
    render() {
        const markup = {__html: this.state.html};
        let className = 'item-view';
        if (!this.props.postRender && this.state.mathjax)
            className += ' mj-typeset'
        return <div className={className} dangerouslySetInnerHTML={markup} />;
    }
}
