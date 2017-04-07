'use strict';

const mjAPI = require('mathjax-node');
const mjConfig = require('./mathjax-config');

mjAPI.config(mjConfig);
mjAPI.start();

mjAPI.typeset({
    math: 'x',
    format: 'TeX',
    html: true,
    css: true
}, function (data) {
    if (!data.errors) {
        console.log(data.css);
    }
});
