import React from 'react';
import ReactDOM from 'react-dom';
import EditItemForm from './edit-item-form';
import MathJaxReady from './mathjax-ready';
import CHtmlCache from './chtml-cache';

const chtml_cache = new CHtmlCache(),
    container = document.getElementById('edit-item-form'),
    notes = container.querySelector('textarea.edit-notes-box').value,
    body = container.querySelector('textarea.edit-item-box').value,
    linkCancel = container.querySelector('a').href;

ReactDOM.render(
    <EditItemForm notes={notes} body={body} mathjax_ready={MathJaxReady}
        chtml_cache={chtml_cache} linkCancel={linkCancel} />,
    container
);
