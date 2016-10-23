import {flattenDeep, map, uniq} from 'lodash';
import {ITEM_NAMES, AST_TYPES} from './constants';

function item_node_to_html(emit, node, eqns, refs, data) {
    if (node.type === AST_TYPES.text) {
        if (node.value)
            data.has_text = true;
        return emit(node.value);
    }
    if (node.type === AST_TYPES.eqn) {
        const item = eqns[node.eqn];
        if (!item)
            throw new Error('corrupt eqn reference');
        if (item.html)
            return emit(item.html);
        if (!item.error)
            throw new Error('corrupt eqn item');
        node = {type: AST_TYPES.error, reason: item.error};
    }
    if (node.type === AST_TYPES.error) {
        data.errors.push(node.reason);
        return emit('<span class="text-danger">', node.reason, '</span>');
    }

    let tag, error;
    const attr = {};

    switch (node.type) {
        case AST_TYPES.blockquote:
            tag = 'blockquote';
            break;
        case AST_TYPES.br:
            return emit(node.hard ? '<br/>' : '\n');
        case AST_TYPES.code:
            return emit('<code>' + node.value + '</code>');
        case AST_TYPES.codeblock:
            return emit('<pre>' + node.value + '</pre>');
        case AST_TYPES.conceptdef:
            if (data.defined.indexOf(node.concept) < 0) {
                data.defined.push(node.concept);
                tag = 'a';
                attr.href = '#';
            } else
                error = 'concept ' + node.concept + ' defined multiple times';
            break;
        case AST_TYPES.conceptref:
            tag = 'a';
            attr.href = '/concept/' + node.concept;
            break;
        case AST_TYPES.doc:
            tag = '';
            break;
        case AST_TYPES.emph:
            tag = 'em';
            break;
        case AST_TYPES.heading:
            tag = 'h' + node.level;
            break;
        case AST_TYPES.itemref:
            const ref_info = refs[node.item];
            if (!ref_info) {
                error = 'illegal item reference ' + node.item;
            } else if (node.concept && (!ref_info.defines || ref_info.defines.indexOf(node.concept) < 0)) {
                error = 'item ' + node.item + ' does not define ' + node.concept;
            } else {
                let ref_data = data.refs[node.item];
                if (!ref_data)
                    data.refs[node.item] = ref_data = {concepts: {}};
                tag = 'a';
                attr.href = ref_info.url;
                if (node.concept) {
                    attr.href += '#' + node.concept;
                    ref_data.concepts[node.concept] = attr.href;
                } else
                    ref_data.url = attr.href;
            }
            break;
        case AST_TYPES.list:
            tag = node.ordered ? 'ol' : 'ul';
            break;
        case AST_TYPES.listitem:
            tag = 'li';
            break;
        case AST_TYPES.paragraph:
            tag = 'p';
            break;
        case AST_TYPES.ruler:
            return emit('<hr/>');
        case AST_TYPES.strong:
            tag = 'strong';
            break;
        // handled above: eqn, error, text
        default:
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

export default function item_data_to_html(item_type, root, eqns, refs) {
    const item_type_name = ITEM_NAMES[item_type],
        out_items = [],
        data = {defined: [], errors: [], refs: {}, has_text: false},
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
