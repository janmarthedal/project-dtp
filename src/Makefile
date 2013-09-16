all: ../main/static/js/templates.js

../main/static/js/templates.js: handlebars
	cp handlebars/teoremer_templates.js $@

handlebars:
	${MAKE} -C handlebars

clean:
	${MAKE} -C handlebars clean

.PHONY: handlebars clean
