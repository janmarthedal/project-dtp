import html_to_item_dom from './html-to-item-dom';
import markdownify from './markdownify';
import prepare_markdown from './prepare-markdown';

export default function markdown_to_item_dom(text) {
    return prepare_markdown(text)
        .then(prepared =>
            markdownify(prepared.text)
                .then(html => html_to_item_dom(html))
                .then(item_dom => ({
                    document: item_dom.document,
                    eqns: prepared.eqns,
                    tags: item_dom.tags,
                    refs: item_dom.refs,
                }))
        );
}
