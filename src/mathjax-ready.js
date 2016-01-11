import Promise from 'promise';

let resolver;

let MathJaxReady = new Promise((resolve) => {
    resolver = resolve;
})

MathJaxReady._resolve = resolver;

export default MathJaxReady;
