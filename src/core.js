import React from 'react';
import ReactDOM from 'react-dom';
import EditItemForm from './edit-item-form';
import RenderItemBox from './render-item-box';
import CHtmlCache from './chtml-cache';
import Promise from 'promise';

var MathJaxReadyResolve;

window.teoremer = {
    React: React,
    ReactDOM: ReactDOM,
    EditItemForm: EditItemForm,
    RenderItemBox: RenderItemBox,
    CHtmlCache: CHtmlCache,
    MathJaxReady: new Promise((resolve) => {
        MathJaxReadyResolve = resolve;
    })
}

window.MathJax = {
    AuthorInit: function () {
        window.MathJax.Hub.Register.StartupHook('End', function () {
            MathJaxReadyResolve(window.MathJax);
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
