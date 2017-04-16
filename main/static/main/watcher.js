(function(win, doc) {

    if (typeof doc.querySelectorAll === 'function'
            && typeof Array.prototype.forEach === 'function'
            && typeof doc.addEventListener === 'function') {

        var on = false;
        var checks = [];

        function hashCode(str) {
            var hash = 0, i, chr;
            for (i = 0; i < str.length; i++) {
                chr   = str.charCodeAt(i);
                hash  = ((hash << 5) - hash) + chr;
                hash |= 0; // Convert to 32bit integer
            }
            return hash + '|' + str.length;
        };

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

        Array.prototype.forEach.call(doc.querySelectorAll('textarea.watch-field[name]'), function (el) {
            var nameChk = el.getAttribute('name') + '-chk';
            var elChk = el.parentElement.querySelector('input[name="' + nameChk + '"]')
            if (elChk === null) {
                elChk = document.createElement('input');
                elChk.setAttribute('type', 'hidden');
                elChk.setAttribute('name', nameChk);
                elChk.setAttribute('value', hashCode(el.value));
                el.parentElement.appendChild(elChk);
            }
            var hash = elChk.getAttribute('value');                    
            checks.push(function () {
                return hashCode(el.value) === hash;
            });
            el.addEventListener('keyup', check, false);
            el.addEventListener('change', check, false);
        });

        Array.prototype.forEach.call(doc.querySelectorAll('.watch-ok'), function (el) {
            el.addEventListener('click', function (ev) {
                handlerOff();
            }, false);
        });

    }

})(window, document);
