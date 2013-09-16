all: teoremer_templates.js

teoremer_templates.js: *.handlebars helpers.js
	handlebars *.handlebars > $@
	cat helpers.js >> $@

clean:
	rm -f teoremer_templates.js
