import {map} from 'lodash';

const tag_map = {
    'body': 'body',
    'p': 'para',
    'strong': 'strong',
    'em': 'emph',
    'li': 'list-item',
};

const regex_tag_def = /^=([-a-z]+)$/;
const regex_html_header = /^h([1-6])$/;
const regex_item_ref = /^([DTP][1-9]\d*)(?:#([-a-z]+))?$/;

function make_error(reason) {
    return {type: 'error', reason: reason};
}

class TagManager {
    constructor() {
        this.counter = 0;
        this.tags = {};
        this.tagToId = {};
    }
    get_id(tag) {
        if (tag in this.tagToId)
            return this.tagToId[tag];
        const id = ++this.counter;
        this.tagToId[tag] = id;
        this.tags[id] = tag;
        return id;
    }
    get_tag_map() {
        return this.tags;
    }
}

function md_node_to_item_dom(node, tag_manager) {
    let match;
    if (node.nodeType === 1) {
        const item_node = {};
        let children = map(node.childNodes,
                           child => md_node_to_item_dom(child, tag_manager));
        if (node.localName === 'img') {
            const src = node.getAttribute('src') || '';
            if (src.startsWith('/eqn/')) {
                return {
                    type: 'eqn',
                    eqn_id: parseInt(src.substring(5))
                }
            } else {
                return make_error("illegal img source '" + src + "'");
            }
        } else if (node.localName === 'a') {
            const href = node.getAttribute('href') || '';
            if ((match = href.match(regex_tag_def)) != null) {
                item_node.type = 'tag-def';
                item_node.tag_id = tag_manager.get_id(match[1]);
            } else if (href.startsWith('=')) {
                return make_error("illegal concept name '" + tag + "'");
            } else if ((match = href.match(regex_item_ref)) != null) {
                item_node.type = 'item-ref';
                item_node.item = match[1];
                if (match[2])
                    item_node.tag_id = tag_manager.get_id(match[2]);
                if (!children)
                    children = [{type: 'text', value: match[1]}]
            } else {
                return make_error("illegal item reference '" + href + "'");
            }
        } else if (node.localName === 'ul' || node.localName === 'ol') {
            item_node.type = 'list';
            item_node.ordered = node.localName === 'ol';
        } else if ((match = node.localName.match(regex_html_header)) != null) {
            item_node.type = 'header';
            item_node.level = parseInt(match[1]);
        } else if (node.localName in tag_map) {
            item_node.type = tag_map[node.localName];
        } else {
            return make_error('unsupported HTML tag ' + node.localName);
        }
        if (children.length)
            item_node.children = children;
        return item_node;
    } else if (node.nodeType === 3) {
        return {type: 'text', value: node.nodeValue};
    } else {
        return make_error('unsupported HTML node type ' + node.nodeValue);
    }
}

export default function md_dom_to_item_dom(node) {
    const tag_manager = new TagManager(),
        document = md_node_to_item_dom(node, tag_manager);
    return {
        document: document,
        tags: tag_manager.get_tag_map(),
    };
}
