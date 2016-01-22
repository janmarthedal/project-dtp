import MathJaxReady from './mathjax-ready';

window.MathJax = {
    AuthorInit: function () {
        window.MathJax.Hub.Register.StartupHook('End', function () {
            console.log('MathJax ready');
            MathJaxReady._resolve(window.MathJax);
        });
    },
    messageStyle: 'none',
    skipStartupTypeset: false,
    jax: ["input/TeX", "output/CommonHTML"],
    extensions: ["tex2jax.js", "MathMenu.js", "MathZoom.js"],
    TeX: {
        extensions: ["AMSmath.js", "AMSsymbols.js", "noErrors.js", "noUndefined.js"]
    }
}
