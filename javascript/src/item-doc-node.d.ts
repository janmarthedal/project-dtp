interface ItemDocNode {
    type?: string;
    value?: string;            // text, code, code_block
    concept?: string;          // conceptdef, itemref
    eqn?: number;              // eqn
    item?: string;
    info?: string;
    media?: string;            // media
    ordered?: boolean;         // list
    listStart?: number;        // list
    listDelimiter?: string;    // list
    hard?: boolean;
    level?: number;
    reason?: string;           // error
    children?: ItemDocNode[];
}
