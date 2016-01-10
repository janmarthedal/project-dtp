(function (scope) {

    const React = scope.React,
        chtml_cache = new scope.CHtmlCache();

    scope.ReactDOM.render(
        <scope.EditItemForm chtml_cache={chtml_cache} />,
        document.getElementById('edit-item-form')
    );

})(window.teoremer);
