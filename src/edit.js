import React from 'react';
import ReactDOM from 'react-dom';
import EditItemForm from './edit-item-form';
import MathJaxReady from './mathjax-ready';
import CHtmlCache from './chtml-cache';

const chtml_cache = new CHtmlCache(),
    container = document.getElementById('edit-item-form'),
    value = container.querySelector('textarea').value;

ReactDOM.render(
    <EditItemForm body={value} mathjax_ready={MathJaxReady} chtml_cache={chtml_cache} />,
    container
);
