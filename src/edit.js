import React from 'react';
import ReactDOM from 'react-dom';
import Rx from 'rx';
import MathJaxReady from './mathjax-ready';
import CHtmlCache from './chtml-cache';
import EditItemBox from './edit-item-box';
import RenderItemBox from './render-item-box';
import {textToItemData, itemDataToHtml} from './item-data';

const chtml_cache = new CHtmlCache();
const editContainer = document.getElementById('edit-item-box');
const initBody = editContainer.querySelector('textarea').value;
const renderContainer = document.getElementById('render-item-box');
const inputStream = new Rx.Subject();
let updateMathJax = false;

function postRender() {
    if (updateMathJax) {
        MathJaxReady.then(MathJax => {
            MathJax.Hub.Queue(['Typeset', MathJax.Hub, renderContainer]);
            updateMathJax = false;
        });
    }
}

ReactDOM.render(
    <EditItemBox initBody={initBody} onChange={ev => inputStream.onNext(ev.target.value)} />,
    editContainer
);

const renderItemBox = ReactDOM.render(<RenderItemBox postRender={postRender} />, renderContainer);

inputStream
    .debounce(500)
    .map(input => textToItemData(input))
    .map(data => itemDataToHtml(data, chtml_cache))
    .forEach(html => {
        updateMathJax = html.mathjax;
        renderItemBox.setState(html)
    });

inputStream.onNext(initBody);
