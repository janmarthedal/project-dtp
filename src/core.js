import MathJaxReady from './mathjax-ready';

window.MathJax = {
    AuthorInit: function () {
        window.MathJax.Hub.Register.StartupHook('End', function () {
            console.log('MathJax ready');
            MathJaxReady._resolve(window.MathJax);
        });
    },
    messageStyle: 'none',
    skipStartupTypeset: true,
    jax: ["input/TeX", "output/CommonHTML"],
    extensions: ["tex2jax.js", "MathMenu.js", "MathZoom.js"],
    TeX: {
        extensions: ["AMSmath.js", "AMSsymbols.js", "noErrors.js", "noUndefined.js"]
    }
}

function removeClass(el, removeName) {
    el.className = el.className.split(' ').filter(name => name !== removeName).join(' ');
}

MathJaxReady.then(MathJax => {
    Array.prototype.forEach.call(document.body.querySelectorAll('.mj-typeset'), el => {
        MathJax.Hub.Queue(['Typeset', MathJax.Hub, el]);
        removeClass(el, 'mj-typeset');
    });
});
