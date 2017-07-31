import * as mjAPI from 'mathjax-node';
import mjConfig from './mathjax-config';

mjAPI.config(mjConfig);
mjAPI.start();

mjAPI.typeset({
    math: 'x',
    format: 'TeX',
    html: true,
    css: true
}, data => {
    if (!data.errors) {
        console.log(data.css);
    }
});
