Handlebars.registerHelper('foreach', function(arr, options) {
    var data;
    return arr.map(function(item, index) {
        if (options.data) {
            data = Handlebars.createFrame(options.data || {});
            data.index = index;
            data.first = index === 0;
            data.last  = index === arr.length-1;
        }
        return options.fn(item, { data: data });
    }).join('');
});