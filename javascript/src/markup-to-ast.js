import commonmark from 'commonmark';
import {AST_TYPES} from './constants';

const reader = new commonmark.Parser();
const regex_tag_def = /^=([-a-z]+)$/;
const regex_item_ref = /^([DTP][1-9]\d*)(?:#([-a-z]+))?$/;
const regex_concept_ref = /^#([-a-z]+)$/;

function make_error(reason) {
    return {
        type: AST_TYPES.error,
        reason: reason
    };
}

function make_text(value) {
    return {
        type: AST_TYPES.text,
        value: value
    };
}

function image_handler(node, item) {
    const src = node.destination || '';
    if (src.startsWith('/eqn/')) {
        return {
            type: AST_TYPES.eqn,
            eqn: parseInt(src.substr(5))
        }
    } else {
        return make_error("illegal img source '" + src + "'");
    }
}

function link_handler(node, item) {
    const href = node.destination || '';
    let match;
    if ((match = href.match(regex_tag_def)) != null) {
        item.type = AST_TYPES.conceptdef;
        item.concept = match[1];
        if (!item.children)
            item.children = [make_text(match[1])];
    } else if (href.startsWith('=')) {
        return make_error("illegal concept name '" + href.substr(1) + "'");
    } else if ((match = href.match(regex_item_ref)) != null) {
        item.type = AST_TYPES.itemref;
        item.item = match[1];
        if (match[2])
            item.concept = match[2];
        if (!item.children)
            item.children = [make_text(match[2] || match[1])];
    } else if ((match = href.match(regex_concept_ref)) != null) {
        item.type = AST_TYPES.conceptref;
        item.concept = match[1];
        if (!item.children)
            item.children = [make_text(match[1])];
    } else {
        return make_error("illegal item reference '" + href + "'");
    }
    return item;
}

function node_visit(node) {
    let item = {};
    const children = [];
    for (let child = node.firstChild; child; child = child.next) {
        let child_item = node_visit(child);
        if (children.length && child_item.type === AST_TYPES.text
                && children[children.length-1].type === AST_TYPES.text) {
            children[children.length-1].value += child_item.value;
        } else
            children.push(child_item);
    }
    if (children.length)
        item.children = children;
    switch (node.type) {
        case 'block_quote':
            item.type = AST_TYPES.blockquote;
            break;
        case 'code':
            item.type = AST_TYPES.code;
            item.value = node.literal;
            break;
        case 'code_block':
            item.type = AST_TYPES.codeblock;
            item.value = node.literal;
            if (node.info)
                item.info = node.info;
            break;
        case 'html_inline':
        case 'html_block':
        case 'text':
            item.type = AST_TYPES.text;
            item.value = node.literal;
            break;
        case 'document':
            item.type = AST_TYPES.doc;
            break;
        case 'emph':
            item.type = AST_TYPES.emph;
            break;
        case 'hardbreak':
            item.hard = true;
        case 'softbreak':
            item.type = AST_TYPES.br;
            break;
        case 'heading':
            item.level = node.level;
            item.type = AST_TYPES.heading;
            break;
        case 'image':
            item = image_handler(node, item);
            break;
        case 'link':
            item = link_handler(node, item);
            break;
        case 'item':
            item.type = AST_TYPES.listitem;
            break;
        case 'list':
            item.ordered = node.listType === 'ordered';
            if (item.ordered) {
                if (node.listStart !== 1)
                    item.listStart = node.listStart;
                item.listDelimiter = node.listDelimiter;
            }
            item.type = AST_TYPES.list;
            break;
        case 'paragraph':
            item.type = AST_TYPES.paragraph;
            break;
        case 'thematic_break':
            item.type = AST_TYPES.ruler;
            break;
        default:
            throw new Error('Unsupported tag ' + node.type);
    }
    return item;
}

export default function markup_to_ast(html) {
    return node_visit(reader.parse(html));
}
