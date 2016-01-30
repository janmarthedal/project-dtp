import React from 'react';

export default class extends React.Component {
    constructor(props) {
        super(props);
        this.state = {};
    }
    render() {
        const concepts = (this.state.defined || []).join(' ');
        const refs = (this.state.item_refs || []).join(' ');
        const eqn_count = Object.keys(this.state.eqns || {}).length;
        return (
            <div>
                <p>Concepts defined: {concepts}</p>
                <p>Items referenced: {refs}</p>
                <p>Distinct equations: {eqn_count}</p>
            </div>
        );
    }
}
