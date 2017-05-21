(function (doc) {

    if (typeof doc.querySelectorAll === 'function'
            && typeof Array.prototype.forEach === 'function'
            && typeof doc.addEventListener === 'function') {
        Array.prototype.forEach.call(doc.querySelectorAll('form.one-click-upload'), function (el) {
            var input = el.querySelector('input[type="file"]');
            var submit = el.querySelector('[type="submit"]');
            input.style.display = 'none';
            submit.addEventListener('click', function (e) {
                e.preventDefault();
                input.click();
            });
            input.addEventListener('change', function () {
                el.submit();
            });
        });
    }

})(document);
