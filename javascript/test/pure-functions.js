import {assert} from 'chai';
import {normalizeTeX} from '../pure-fun';

describe('Pure functions', function() {
    it('normalizeTeX', function() {
        assert.equal('\\sin(x)+b', normalizeTeX(' \\sin ( x) +  b'));
        assert.equal('\\sum_{k=1}^nk', normalizeTeX('\\sum_{k = 1}^n k'));
    });
});

/*    describe('eqn-typeset', function() {
        function tester(key, format, math, html, done) {
            eqn_typeset(key, {format:format, math:math}).then(ret => {
                assert.equal(ret[0], key);
                assert.equal(ret[1].format, format);
                assert.equal(ret[1].math, math);
                assert.equal(ret[1].html, html);
                done();
            });
        }
        it('1', function(done) {
            tester('key-1', "TeX", "\\sum_{k=1}^n k", '<span class="mjx-chtml MJXc-display" style="text-align: center;"><span id="MathJax-Element-1-Frame" class="mjx-chtml"><span id="MJXc-Node-1" class="mjx-math" role="math"><span id="MJXc-Node-2" class="mjx-mrow"><span id="MJXc-Node-3" class="mjx-munderover"><span class="mjx-itable"><span class="mjx-row"><span class="mjx-cell"><span class="mjx-stack"><span class="mjx-over" style="font-size: 70.7%; padding-bottom: 0.247em; padding-top: 0.141em; padding-left: 0.721em;"><span id="MJXc-Node-10" class="mjx-mi" style=""><span class="mjx-char MJXc-TeX-math-I" style="padding-top: 0.225em; padding-bottom: 0.298em;">n</span></span></span><span class="mjx-op"><span id="MJXc-Node-4" class="mjx-mo"><span class="mjx-char MJXc-TeX-size2-R" style="padding-top: 0.74em; padding-bottom: 0.74em;">∑</span></span></span></span></span></span><span class="mjx-row"><span class="mjx-under" style="font-size: 70.7%; padding-top: 0.236em; padding-bottom: 0.141em; padding-left: 0.122em;"><span id="MJXc-Node-5" class="mjx-texatom" style=""><span id="MJXc-Node-6" class="mjx-mrow"><span id="MJXc-Node-7" class="mjx-mi"><span class="mjx-char MJXc-TeX-math-I" style="padding-top: 0.446em; padding-bottom: 0.298em;">k</span></span><span id="MJXc-Node-8" class="mjx-mo"><span class="mjx-char MJXc-TeX-main-R" style="padding-top: 0.077em; padding-bottom: 0.298em;">=</span></span><span id="MJXc-Node-9" class="mjx-mn"><span class="mjx-char MJXc-TeX-main-R" style="padding-top: 0.372em; padding-bottom: 0.372em;">1</span></span></span></span></span></span></span></span><span id="MJXc-Node-11" class="mjx-mi MJXc-space1"><span class="mjx-char MJXc-TeX-math-I" style="padding-top: 0.446em; padding-bottom: 0.298em;">k</span></span></span></span></span></span>', done);
        });
    });
});

describe('Render item', function() {
    it('item-dom-to-html', function(done) {
        item_dom_to_html('D', {"type":"body"}, {}, {}).then(ret => {
            assert.lengthOf(ret.defined, 0);
            assert.isNotOk(ret.has_text);
            assert.strictEqual(ret.html, '');
            assert.include(ret.errors, 'A Definition may not be empty');
            assert.include(ret.errors, 'A Definition must define at least one concept');
            assert.lengthOf(ret.errors, 2);
            done();
        });
    });
});
*/
