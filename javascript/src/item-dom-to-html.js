function item_node_to_html(emit, node, eqns) {
    if (node.type === 'text')
        return emit(node.value);
    if (node.type === 'eqn') {
        const item = eqns[node.id];
        if (!item)
            throw new Error('corrupt eqn reference');
        if (item.html)
            return emit(item.html);
        if (item.error)
            node = {type: 'error', reason: item.error};
        else
            throw new Error('corrupt eqn item');
    }
    if (node.type === 'error') {
        emit('<span class="text-danger">');
        emit(node.reason);
        emit('</span>');
        return;
    }
    let start, stop;
    switch (node.type) {
        case 'body':
            break;
        case 'para':
            start = '<p>'; stop = '</p>'; break;
        case 'strong':
            start = '<strong>'; stop = '</strong>'; break;
        case 'emph':
            start = '<em>'; stop = '</em>'; break;
        case 'tag-def':
            start = '<a href="#">'; stop = '</a>'; break;
        case 'list':
            if (node.ordered) {
                start = '<ol>'; stop = '</ol>';
            } else {
                start = '<ul>'; stop = '</ul>';
            }
            break;
        case 'list-item':
            start = '<li>'; stop = '</li>'; break;
        case 'header': {
            const tag = 'h' + node.level;
            start = '<' + tag + '>'; stop = '</' + tag + '>';
            break;
        }
        default:
            throw new Error('Unsupported node type \'' + node.type + '\'');
    }
    if (start)
        emit(start);
    if (node.children)
        node.children.forEach(child => item_node_to_html(emit, child, eqns))
    if (stop)
        emit(stop);
}

export default function item_dom_to_html(root, eqns) {
    const out_items = [],
        emit = item => { out_items.push(item) };
    item_node_to_html(emit, root, eqns || {});
    return Promise.resolve(out_items.join(''));
}
