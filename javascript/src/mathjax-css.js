'use strict';

var mjAPI = require("mathjax-node/lib/mj-single.js");

mjAPI.config({MathJax: {}});
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
