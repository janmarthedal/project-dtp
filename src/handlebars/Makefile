all: teoremer_handlebars.js

teoremer_handlebars.js: *.handlebars helpers.js
	handlebars *.handlebars > $@
	cat helpers.js >> $@

clean:
	rm -f teoremer_handlebars.js

