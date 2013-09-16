(function(window) {

    window.teoremer.page = {
        source_list: function(elem, items) {
            new teoremer.SourceListView({
                el: $(elem),
                collection: new teoremer.SourceList(items)
            });
        }
    };

})(window);