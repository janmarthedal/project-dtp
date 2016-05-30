import jsdom from 'jsdom';
import md_dom_to_item_dom from './md-dom-to-item-dom';

export default function html_to_item_dom(html) {
    return new Promise(function (resolve, reject) {
        jsdom.env(html, function (err, window) {
            if (!err) {
                const body = window.document.body;
                const item_dom = md_dom_to_item_dom(body);
                window.close();
                resolve(item_dom);
            } else {
                reject(err);
            }
        });
    });
}
