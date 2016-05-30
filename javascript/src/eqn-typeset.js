import mjAPI from 'mathjax-node/lib/mj-single';

mjAPI.config({MathJax: {}});
mjAPI.start();

export default function typeset(id, data) {
    if (data.error)
        return Promise.resolve([id, data]);
    if (['TeX', 'inline-TeX'].indexOf(data.format) < 0)
        return Promise.reject('illegal typeset format');
    return new Promise((resolve, reject) => {
        mjAPI.typeset({
            math: data.math,
            format: data.format,
            html: true,
        }, result => {
            resolve([id, result.errors ? {error: result.errors} : {html: result.html}]);
        });
    });
}
