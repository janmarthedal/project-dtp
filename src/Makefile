all: ../main/static/js/teoremer.js

../main/static/js/teoremer.js: js/teoremer.js handlebars
	cat js/teoremer.js handlebars/teoremer_handlebars.js > $@

handlebars:
	${MAKE} -C handlebars

clean:
	${MAKE} -C handlebars clean

.PHONY: handlebars clean

