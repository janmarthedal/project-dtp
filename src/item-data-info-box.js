import React from 'react';

export default class extends React.Component {
    constructor(props) {
        super(props);
        this.state = {};
    }
    render() {
        const concept_map = this.state.concept_map || {};
        const item_ref_map = this.state.item_refs || {};
        const con_defs = (this.state.concept_defs || []).map(id => concept_map[id]).join(' ');
        const con_refs = (this.state.concept_refs || []).map(id => concept_map[id]).join(' ');
        const item_refs = Object.keys(item_ref_map).map(id => item_ref_map[id]).join(' ');
        const eqn_count = Object.keys(this.state.eqns || {}).length;
        return (
            <div>
                <p>Concepts defined: {con_defs}</p>
                <p>Concepts referenced: {con_refs}</p>
                <p>Items referenced: {item_refs}</p>
                <p>Distinct equations: {eqn_count}</p>
            </div>
        );
    }
}
