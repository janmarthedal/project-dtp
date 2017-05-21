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

        /* helpers */

        function forEach(arr, fn) {
            Array.prototype.forEach.call(arr, fn);
        }

        /* watcher */

        let on = false;
        const checks = [];

        function hashCode(str) {
            let hash = 0;
            for (let i = 0; i < str.length; i++) {
                hash  = ((hash << 5) - hash) + str.charCodeAt(i);
                hash |= 0; // Convert to 32bit integer
            }
            return hash + '|' + str.length;
        };

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

        forEach(doc.querySelectorAll('textarea.watch-field[name]'), el => {
            const nameChk = el.getAttribute('name') + '-chk';
            let elChk = el.parentElement.querySelector('input[name="' + nameChk + '"]')
            if (elChk === null) {
                elChk = document.createElement('input');
                elChk.setAttribute('type', 'hidden');
                elChk.setAttribute('name', nameChk);
                elChk.setAttribute('value', hashCode(el.value));
                el.parentElement.appendChild(elChk);
            }
            const hash = elChk.getAttribute('value');                    
            checks.push(() => hashCode(el.value) === hash);
            el.addEventListener('keyup', check, false);
            el.addEventListener('change', check, false);
        });

        forEach(doc.querySelectorAll('.watch-ok'), el => {
            el.addEventListener('click', function () {
                handlerOff();
            }, false);
        });

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
