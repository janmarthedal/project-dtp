function item_node_to_html(node, eqns) {
    if (node.type === 'text')
        return node.value;
    if (node.type === 'eqn') {
        let item = eqns[node.id];
        if (!item)
            item = {error: 'corrupt eqn reference'};
        if (item.error)
            return '<span class="text-danger">' + item.error + '</span>';
        return item.html;
    }
    if (node.type === 'error')
        return '<span class="text-danger">' + node.reason + '</span>';
    const children = (node.children || [])
        .map(child => item_node_to_html(child, eqns))
        .join('');
    if (node.type === 'body')
        return children;
    if (node.type === 'para')
        return '<p>' + children + '</p>';
    if (node.type === 'strong')
        return '<strong>' + children + '</strong>';
    if (node.type === 'emph')
        return '<em>' + children + '</em>';
    if (node.type === 'tag-def')
        return '<a href="#">' + children + '</a>';
    if (node.type === 'list')
        return node.ordered ? '<ol>' + children + '</ol>' : '<ul>' + children + '</ul>';
    if (node.type === 'list-item')
        return '<li>' + children + '</li>';
    if (node.type === 'header') {
        const tag = 'h' + node.level;
        return '<' + tag + '>' + children + '</' + tag + '>';
    }
    return '<span class="text-danger">unsupported node type \'' + node.type + "'";
}

export default function item_dom_to_html(root, eqns) {
    return Promise.resolve(item_node_to_html(root, eqns || {}));
}
