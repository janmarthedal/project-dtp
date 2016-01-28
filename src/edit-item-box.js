import React from 'react';

export default ({onChange, initBody}) => (
    <textarea name="body" className="edit-item-box pure-input-1"
        onChange={onChange}
        defaultValue={initBody}
     />
);
