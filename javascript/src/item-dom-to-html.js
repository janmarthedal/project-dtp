import {flattenDeep, map, uniq} from 'lodash';

const type_to_tag = {
    'body': '',
    'para': 'p',
    'strong': 'strong',
    'emph': 'em',
    'list-item': 'li',
};

function item_node_to_html(emit, node, eqns, tags, data) {
    if (node.type === 'text')
        return emit(node.value);
    if (node.type === 'eqn') {
        const item = eqns[node.eqn_id];
        if (!item)
            throw new Error('corrupt eqn reference');
        if (item.html)
            return emit(item.html);
        if (!item.error)
            throw new Error('corrupt eqn item');
        node = {type: 'error', reason: item.error};
    }
    if (node.type === 'error') {
        data.errors.push(node.reason);
        return emit('<span class="text-danger">', node.reason, '</span>');
    }

    let tag, attr = {};
    if (node.type in type_to_tag) {
        tag = type_to_tag[node.type];
    } else if (node.type === 'tag-def') {
        if (data.defined.indexOf(node.tag_id) < 0)
            data.defined.push(node.tag_id);
        else
            data.errors.push('tag \'' + tags[node.tag_id] + '\' defined multiple times');
        tag = 'a';
        attr.href = '#';
    } else if (node.type === 'list') {
        tag = node.ordered ? 'ol' : 'ul';
    } else if (node.type === 'header') {
        tag = 'h' + node.level;
    } else {
        throw new Error('Unsupported node type \'' + node.type + '\'');
    }
    if (tag)
        emit('<', tag, map(attr, (value, key) => [' ', key, '="', value, '"']), '>');
    if (node.children)
        node.children.forEach(child => item_node_to_html(emit, child, eqns, tags, data))
    if (tag)
        emit('</', tag, '>');
}

export default function item_dom_to_html(root, eqns, tags) {
    const out_items = [],
        data = {defined: [], errors: []},
        emit = (...items) => {
            Array.prototype.push.apply(out_items, items);
        };
    item_node_to_html(emit, root, eqns, tags, data);
    data.html = flattenDeep(out_items).join('');
    data.errors = uniq(data.errors);
    return Promise.resolve(data);
}
