import json_parse_relax_keys from './json-parse-relax-keys';
import {JSDOM} from 'jsdom';

const rx_code = /^\s*createCindy\s*\(\s*([\s\S]*?)\s*\)(\s*;)?\s*$/;

export default function (html_file) {
    return JSDOM.fromFile(html_file).then(dom => {
        const external_js = dom.window.document.querySelectorAll('script[type="text/javascript"][src]') as NodeListOf<HTMLScriptElement>;
        const inline_js = dom.window.document.querySelectorAll('script[type="text/javascript"]:not([src])');
        if (external_js.length === 0) {
            return {error: 'No library import'};
        }
        if (external_js.length > 1) {
            return {error: 'Multiple library imports'};
        }
        if (inline_js.length !== 1) {
            return {error: 'No initializer code'};
        }
        const code_match = inline_js[0].textContent.match(rx_code);
        if (!code_match) {
            return {error: 'Illegal initializer code'};
        }
        let init_data;
        try {
            init_data = json_parse_relax_keys(code_match[1]);
        } catch (ex) {
            return {error: 'Illegal initializer data'};
        }
        return {
            title: dom.window.document.querySelector("head>title").textContent,
            lib: external_js[0].src,
            data: init_data
        };
    });
};