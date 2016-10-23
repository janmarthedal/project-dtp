import prepare_markup from './prepare-markup';
import markup_to_ast from './markup-to-ast';

export default function markup_to_item_data(text) {
    const prepared = prepare_markup(text);
    const ast = markup_to_ast(prepared.text);
    return Promise.resolve({
        document: ast,
        eqns: prepared.eqns
    });
}
