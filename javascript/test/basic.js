import {assert} from 'chai';
import {normalizeTeX} from '../pure-fun';
import markdown_to_item_dom from '../markdown-to-item-dom';

describe('Pure functions', () => {
    it('normalizeTeX', () => {
        assert.equal('\\sin(x)+b', normalizeTeX(' \\sin ( x) +  b'));
        assert.equal('\\sum_{k=1}^nk', normalizeTeX('\\sum_{k = 1}^n k'));
    });
});

describe('Prepare items', () => {
    it('markdown-to-item-dom', done => {
        markdown_to_item_dom(
`Inline math $x$ and

$$
\\sum_{k=1}^n k
$$

More $x$ inline $a+b$ math.`
        ).then(item_dom => {
            assert.deepEqual(
                {"document":{"type":"body","children":[
                    {"type":"para","children":[
                        {"type":"text","value":"Inline math "},{"type":"eqn","eqn":1},{"type":"text","value":" and"}
                    ]},{"type":"text","value":"\n"},{"type":"para","children":[
                        {"type":"eqn","eqn":2}]},{"type":"text","value":"\n"},{"type":"para","children":[
                            {"type":"text","value":"More "},{"type":"eqn","eqn":1},{"type":"text","value":" inline "},
                            {"type":"eqn","eqn":3},{"type":"text","value":" math."}
                        ]},{"type":"text","value":"\n"}
                    ]},
                "eqns":{
                    "1":{"format":"inline-TeX","math":"x"},
                    "2":{"format":"TeX","math":"\\sum_{k=1}^nk"},
                    "3":{"format":"inline-TeX","math":"a+b"}}}, item_dom);
            done();
        });
    });
});
