import React from 'react';
import ReactDOM from 'react-dom';
import {Subject} from './rx';
//import Rx from 'rx';
//const Subject = Rx.Subject;
import MathJaxReady from './mathjax-ready';
import CHtmlCache from './chtml-cache';
import EditItemBox from './edit-item-box';
import RenderItemBox from './render-item-box';
import ItemDataInfoBox from './item-data-info-box';
import {textToItemData, itemDataToHtml} from './item-data';

const chtml_cache = new CHtmlCache();
const editContainer = document.getElementById('edit-item-box');
const renderContainer = document.getElementById('render-item-box');
const initBody = editContainer.querySelector('textarea').value;
const inputStream = new Subject();
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

const renderItemBox = ReactDOM.render(
    <RenderItemBox postRender={postRender} />,
    renderContainer
);

const itemDataInfoBox = ReactDOM.render(
    <ItemDataInfoBox />,
    document.getElementById('item-data-info-box')
);

const itemDataStream = inputStream
    .debounce(500)
    .startWith(initBody)
    .map(input => textToItemData(input));

itemDataStream.subscribe(data => {
    itemDataInfoBox.setState(data);
});

itemDataStream
    .map(data => itemDataToHtml(data, chtml_cache))
    .subscribe(html => {
        updateMathJax = html.mathjax;
        renderItemBox.setState(html)
    });
