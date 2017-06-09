/* google analytics */

window.ga=function(){ga.q.push(arguments)};
ga.q=[];
ga.l=+new Date;
ga('create','UA-46471633-3','auto');
ga('send','pageview');

(function(win, doc) {

    if (typeof doc.querySelectorAll === 'function'
            && typeof Array.prototype.forEach === 'function'
            && typeof doc.addEventListener === 'function') {
        
        const page_data_script = doc.querySelector('script[type="x-mathitems"]');
        const page_data = page_data_script ? JSON.parse(page_data_script.text) : {};

        /* helpers */

        function forEach(arr, fn) {
            Array.prototype.forEach.call(arr, fn);
        }

        /* watcher */

        if (page_data.watch) {

            let on = false;
            const checks = [];

            function unloadHandler(ev) {
                const msg = 'You have unsaved changes';
                ev.returnValue = msg;
                return msg;
            }

            function handlerOn() {
                win.addEventListener('beforeunload', unloadHandler, false);
            }

            function handlerOff() {
                win.removeEventListener('beforeunload', unloadHandler, false);
            }

            function check() {
                let changed = false;
                checks.forEach(isSame => {
                    changed = changed || !isSame();
                });
                if (changed != on) {
                    (changed ? handlerOn : handlerOff)();
                    on = changed;
                }
            }

            forEach(page_data.watch.elements, item => {
                const el = doc.querySelector(item.el);
                const saved = typeof item.value === 'string' ? item.value : el.value;
                checks.push(() => el.value === saved);
                el.addEventListener('keyup', check, false);
                el.addEventListener('change', check, false);
            });

            forEach(page_data.watch.allow, sel => {
                doc.querySelector(sel).addEventListener('click', function () {
                    handlerOff();
                }, false);
            });

            check();
        }

        /* one click upload */

        forEach(doc.querySelectorAll('form.one-click-upload'), el => {
            const input = el.querySelector('input[type="file"]');
            const submit = el.querySelector('[type="submit"]');
            input.style.display = 'none';
            submit.addEventListener('click', e => {
                e.preventDefault();
                input.click();
            });
            input.addEventListener('change', () => {
                el.submit();
            });
        });

    }

})(window, document);
