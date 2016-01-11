import React from 'react';
import ReactDOM from 'react-dom';
import EditItemForm from './edit-item-form';
import CHtmlCache from './chtml-cache';

let chtml_cache = new CHtmlCache();

ReactDOM.render(
    <EditItemForm chtml_cache={chtml_cache} />,
    document.getElementById('edit-item-form')
);
