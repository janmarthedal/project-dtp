
const tag_map = {
    'body': 'body',
    'p': 'para',
    'strong': 'strong',
    'em': 'emph',
    'li': 'list-item',
};

const regex_tag_def = /^=[-a-z]+$/;
const regex_html_header = /^h([1-6])$/;

function make_error(reason) {
    return {type: 'error', reason: reason};
}

export default function md_dom_to_item_dom(node) {
    let match;
    if (node.nodeType === 1) {
        const item_node = {};
        const children = Array.prototype.map.call(node.childNodes, child => md_dom_to_item_dom(child));
        if (node.localName === 'img') {
            const src = node.getAttribute('src') || '';
            if (src.startsWith('/eqn/')) {
                return {
                    type: 'eqn',
                    id: parseInt(src.substring(5))
                }
            } else {
                return make_error("illegal img source '" + src + "'");
            }
        } else if (node.localName === 'a') {
            const href = node.getAttribute('href') || '';
            if (regex_tag_def.test(href)) {
                item_node.type = 'tag-def';
                item_node.tag = href.substring(1);
            } else if (href.startsWith('=')) {
                return make_error("illegal tag '" + tag + "'");
            } else {
                return make_error("illegal item reference '" + href + "'");
            }
        } else if (node.localName === 'ul' || node.localName === 'ol') {
            item_node.type = 'list';
            item_node.ordered = node.localName === 'ol';
        } else if (!!(match = node.localName.match(regex_html_header))) {
            item_node.type = 'header';
            item_node.level = parseInt(match[1]);
        } else if (node.localName in tag_map) {
            item_node.type = tag_map[node.localName];
        } else {
            return make_error('unsupported HTML tag ' + node.localName);
        }
        if (children.length)
            item_node.children = children
        return item_node;
    } else if (node.nodeType === 3) {
        return {
            type: 'text',
            value: node.nodeValue
        }
    } else {
        return make_error('unsupported HTML node type ' + node.nodeValue);
    }
}
