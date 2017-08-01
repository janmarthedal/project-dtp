/// <reference path="item-doc-node.d.ts" />

import {flattenDeep, map, uniq} from 'lodash';
import {ITEM_NAMES, AST_TYPES} from './constants';

interface RefInfo {
    url?: string;
    concepts: {[key:string]:string};
}

class Converter {
    // input
    private readonly item_type: string;
    private readonly eqns;
    private readonly concepts;
    private readonly item_info;
    private readonly media;

    // state
    private readonly out_items = [];
    private is_empty: boolean = true;

    // output
    private readonly defined: string[] = [];
    private readonly errors: string[] = [];
    private readonly refs: { [key: string]: RefInfo } = {};
    private readonly concept_refs: { [key: string]: string; } = {};

    constructor(item_type, eqns, concepts, item_info, media) {
        this.item_type = item_type;
        this.eqns = eqns;
        this.concepts = concepts;
        this.item_info = item_info;
        this.media = media;
    }

    private emit(...items) {
        Array.prototype.push.apply(this.out_items, items);
    }

    convert_node(node: ItemDocNode) {
        if (node.type === AST_TYPES.text) {
            if (node.value)
                this.is_empty = false;
            return this.emit(node.value);
        }
        if (node.type === AST_TYPES.eqn) {
            const item = this.eqns[node.eqn];
            this.is_empty = false;
            if (!item)
                throw new Error('corrupt eqn reference');
            if (item.html)
                return this.emit(item.html);
            if (!item.error)
                throw new Error('corrupt eqn item');
            node = {type: AST_TYPES.error, reason: item.error};
        }
        if (node.type === AST_TYPES.error) {
            this.errors.push(node.reason);
            return this.emit('<span class="error">', node.reason, '</span>');
        }

        let tag, error;
        const attr: {
            href?: string;
            start?: number;
            'class'?: string;
        } = {};
        const class_names = [];
        const concept_name = node.concept ? this.concepts[node.concept] : undefined;

        switch (node.type) {
            case AST_TYPES.blockquote:
                tag = 'blockquote';
                break;
            case AST_TYPES.br:
                return this.emit(node.hard ? '<br/>' : '\n');
            case AST_TYPES.code:
                return this.emit('<code>' + node.value + '</code>');
            case AST_TYPES.codeblock:
                return this.emit('<pre>' + node.value + '</pre>');
            case AST_TYPES.conceptdef:
                if (this.defined.indexOf(node.concept) < 0) {
                    this.defined.push(node.concept);
                    tag = 'a';
                    attr.href = '/concept/' + concept_name;
                    class_names.push('concept-def');
                } else
                    error = 'concept ' + concept_name + ' defined multiple times';
                break;
            case AST_TYPES.conceptref:
                tag = 'a';
                attr.href = '/concept/' + concept_name;
                class_names.push('concept-ref');
                this.concept_refs[concept_name] = attr.href;
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
                const ref_info = this.item_info[node.item];
                if (!ref_info) {
                    error = 'illegal item reference ' + node.item;
                } else if (node.concept && (!ref_info.defines || ref_info.defines.indexOf(concept_name) < 0)) {
                    error = 'item ' + node.item + ' does not define ' + concept_name;
                } else {
                    let ref_data = this.refs[node.item];
                    if (!ref_data)
                        this.refs[node.item] = ref_data = {concepts: {}};
                    tag = 'a';
                    attr.href = ref_info.url;
                    class_names.push('item-ref');
                    if (node.concept) {
                        attr.href += '#' + concept_name;
                        ref_data.concepts[concept_name] = attr.href;
                    } else
                        ref_data.url = attr.href;
                }
                break;
            case AST_TYPES.list:
                tag = node.ordered ? 'ol' : 'ul';
                if (typeof node.listStart === 'number' && node.listStart !== 1)
                    attr.start = node.listStart;
                break;
            case AST_TYPES.listitem:
                tag = 'li';
                break;
            case AST_TYPES.media:
                const media_tag = this.media[node.media];
                if (media_tag)
                    return this.emit('<figure class="item-img">', media_tag,
                        '<figcaption>', node.media, '</figcaption></figure>');
                error = 'Illegal media reference ' + node.media;
                break;
            case AST_TYPES.paragraph:
                tag = 'p';
                break;
            case AST_TYPES.ruler:
                return this.emit('<hr/>');
            case AST_TYPES.strong:
                tag = 'strong';
                break;
            // handled above: eqn, error, text
            default:
                throw new Error('Unsupported node type \'' + node.type + '\'');
        }

        if (error) {
            this.errors.push(error);
            return this.emit('<span class="error">', error, '</span>');
        }
        if (tag) {
            if (class_names.length)
                attr['class'] = class_names.join(' ');
            this.emit('<', tag, map(attr, (value, key) => [' ', key, '="', value, '"']), '>');
        }
        if (node.children)
            node.children.forEach(child => this.convert_node(child));
        this.emit('</', tag, '>');
    }

    get_result() {
        const item_type_name = ITEM_NAMES[this.item_type];
        if (this.is_empty)
            this.errors.push('A ' + item_type_name + ' may not be empty')
        if (this.item_type === 'D' && !this.defined.length)
            this.errors.push('A ' + item_type_name + ' must define at least one concept')
        if (this.item_type !== 'D' && this.defined.length)
            this.errors.push('A ' + item_type_name + ' may not define concepts')
        return {
            defined: map(this.defined, concept_id => this.concepts[concept_id]),
            errors: uniq(this.errors),
            refs: this.refs,
            concept_refs: this.concept_refs,
            html: flattenDeep(this.out_items).join(''),
        };
    }
}

export default function item_data_to_html(item_type, root, eqns, concepts, refs, media) {
    const converter = new Converter(item_type, eqns, concepts, refs, media);
    converter.convert_node(root);
    return Promise.resolve(converter.get_result());
}
