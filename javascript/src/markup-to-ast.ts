/// <reference path="item-doc-node.d.ts" />

import * as commonmark from 'commonmark';
import * as last from 'lodash/last';
import {AST_TYPES} from './constants';

const reader = new commonmark.Parser();
const regex_tag_def = /^=([-\/a-zA-Z]+)$/;
const regex_item_ref = /^([DTP][1-9]\d*)(?:#([-\/a-zA-Z]+))?$/;
const regex_concept_ref = /^#([-\/a-zA-Z]+)$/;
const regex_media_ref = /^(M[1-9]\d*)$/;

class ConceptMap {
    private counter = 0;
    private readonly idToCon = {};
    private readonly conToId = {};
    get_id(con) {
        if (con in this.conToId)
            return this.conToId[con];
        const id = ++this.counter;
        this.conToId[con] = id;
        this.idToCon[id] = con;
        return id;
    }
    get_concept_map() {
        return this.idToCon;
    }
}

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

// keep in sync with function in mathitems/models.py
function concept_to_label(con: string) {
    const r = last(con.split('/'));
    return r ? r.replace(/-/g, ' ') : con;
}

function image_handler(node): ItemDocNode {
    const src = node.destination || '';
    let match;
    if ((match = src.match(regex_media_ref)) != null) {
        return {
            type: AST_TYPES.media,
            media: match[1],
            ...node.title && {caption: node.title}
        };
    } else if (src.startsWith('/eqn/')) {
        return {
            type: AST_TYPES.eqn,
            eqn: parseInt(src.substr(5))
        };
    } else {
        return make_error("illegal img source '" + src + "'");
    }
}

function link_handler(node, item: ItemDocNode, concept_map) {
    const href = node.destination || '';
    let match;
    if ((match = href.match(regex_tag_def)) != null) {
        item.type = AST_TYPES.conceptdef;
        item.concept = concept_map.get_id(match[1]);
        if (!item.children)
            item.children = [make_text(concept_to_label(match[1]))];
    } else if (href.startsWith('=')) {
        return make_error("illegal concept name '" + href.substr(1) + "'");
    } else if ((match = href.match(regex_item_ref)) != null) {
        item.type = AST_TYPES.itemref;
        item.item = match[1];
        if (match[2])
            item.concept = concept_map.get_id(match[2]);
        if (!item.children)
            item.children = [make_text(match[2] ? concept_to_label(match[2]) : match[1])];
    } else if ((match = href.match(regex_concept_ref)) != null) {
        item.type = AST_TYPES.conceptref;
        item.concept = concept_map.get_id(match[1]);
        if (!item.children)
            item.children = [make_text(concept_to_label(match[1]))];
    } else {
        return make_error("illegal item reference '" + href + "'");
    }
    return item;
}

function node_visit(node, concept_map) {
    let item: ItemDocNode = {};
    const children = [];
    for (let child = node.firstChild; child; child = child.next) {
        let child_item = node_visit(child, concept_map);
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
            item = image_handler(node);
            break;
        case 'link':
            item = link_handler(node, item, concept_map);
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
    const concept_map = new ConceptMap();
    const ast = node_visit(reader.parse(html), concept_map);
    return {
        document: ast,
        concepts: concept_map.get_concept_map()
    };
}
