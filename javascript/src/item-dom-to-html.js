import {flattenDeep, map, uniq} from 'lodash';
import {ITEM_NAMES} from './constants';

const type_to_tag = {
    'body': '',
    'para': 'p',
    'strong': 'strong',
    'emph': 'em',
    'list-item': 'li',
};

function item_node_to_html(emit, node, eqns, refs, data) {
    if (node.type === 'text') {
        if (node.value)
            data.has_text = true;
        return emit(node.value);
    }
    if (node.type === 'eqn') {
        const item = eqns[node.eqn];
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

    let tag, error;
    const attr = {};

    if (node.type in type_to_tag) {
        tag = type_to_tag[node.type];
    } else if (node.type === 'concept-def') {
        if (data.defined.indexOf(node.concept) < 0) {
            data.defined.push(node.concept);
            tag = 'a';
            attr.href = '#';
        } else
            error = 'concept ' + node.concept + ' defined multiple times';
    } else if (node.type === 'item-ref') {
        const ref_info = refs[node.item];
        if (!ref_info) {
            error = 'illegal item reference ' + node.item;
        } else if (node.concept && (!ref_info.defines || ref_info.defines.indexOf(node.concept) < 0)) {
            error = 'item ' + node.item + ' does not define ' + node.concept;
        } else {
            tag = 'a';
            attr.href = ref_info.url;
            if (node.concept)
                attr.href += '#' + node.concept;
        }
    } else if (node.type === 'list') {
        tag = node.ordered ? 'ol' : 'ul';
    } else if (node.type === 'header') {
        tag = 'h' + node.level;
    } else {
        throw new Error('Unsupported node type \'' + node.type + '\'');
    }
    if (error) {
        data.errors.push(error);
        return emit('<span class="text-danger">', error, '</span>');
    }
    if (tag)
        emit('<', tag, map(attr, (value, key) => [' ', key, '="', value, '"']), '>');
    if (node.children)
        node.children.forEach(child => item_node_to_html(emit, child, eqns, refs, data))
    if (tag)
        emit('</', tag, '>');
}

export default function item_dom_to_html(item_type, root, eqns, refs) {
    const item_type_name = ITEM_NAMES[item_type],
        out_items = [],
        data = {defined: [], errors: [], has_text: false},
        emit = (...items) => {
            Array.prototype.push.apply(out_items, items);
        };
    item_node_to_html(emit, root, eqns, refs, data);
    data.html = flattenDeep(out_items).join('');
    if (!data.has_text)
        data.errors.push('A ' + item_type_name + ' may not be empty')
    if (item_type === 'D' && !data.defined.length)
        data.errors.push('A ' + item_type_name + ' must define at least one concept')
    if (item_type !== 'D' && data.defined.length)
        data.errors.push('A ' + item_type_name + ' may not define concepts')
    data.errors = uniq(data.errors);
    return Promise.resolve(data);
}
