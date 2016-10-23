import {assert} from 'chai';
import markup_to_ast from '../markup-to-ast';

describe('markup-to-ast', function() {
    it('1', function() {
        const ast = markup_to_ast(
`Inline math $x$ and

$$
\\sum_{k=1}^n k
$$

More $x$ inline $a+b$ math.`
        );
        assert.deepEqual({
            "children": [{
                "children": [{
                    "type": "text",
                    "value": "Inline math $x$ and"
                }],
                "type": "para"
            }, {
                "children": [{
                    "type": "text",
                    "value": "$$"
                }, {
                    "type": "break"
                }, {
                    "type": "text",
                    "value": "\\sum_{k=1}^n k"
                }, {
                    "type": "break"
                }, {
                    "type": "text",
                    "value": "$$"
                }],
                "type": "para"
            }, {
                "children": [{
                    "type": "text",
                    "value": "More $x$ inline $a+b$ math."
                }],
                "type": "para"
            }],
            "type": "document"
        }, ast);
    });
});
