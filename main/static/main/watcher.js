(function(win, doc) {

    if (typeof doc.querySelectorAll === 'function'
            && typeof Array.prototype.forEach === 'function'
            && typeof doc.addEventListener === 'function') {

        function unloadHandler(ev) {
            var msg = 'You have unsaved changes';
            ev.returnValue = msg;
            return msg;
        }

        function handlerOn() {
            win.addEventListener('beforeunload', unloadHandler, false);
        }

        function handlerOff() {
            win.removeEventListener('beforeunload', unloadHandler, false);
        }

        if (doc.querySelector('.watch-all') != null) {
            handlerOn();
        } else {
            var on = false;
            var checks = [];

            function check() {
                var changed = false;
                checks.forEach(function(isSame) {
                    changed = changed || !isSame();
                });
                if (changed != on) {
                    (changed ? handlerOn : handlerOff)();
                    on = changed;
                }
            }

            Array.prototype.forEach.call(doc.querySelectorAll('textarea.watch-field'), function (el) {
                var initVal = el.value;
                checks.push(function() {
                    return el.value === initVal;
                });
                el.addEventListener('keyup', check, false);
                el.addEventListener('change', check, false);
            });
        }

    }

})(window, document);
