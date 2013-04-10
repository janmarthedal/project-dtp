all: ../main/static/js/teoremer.js

../main/static/js/teoremer.js: handlebars/teoremer_handlebars.js js/teoremer.js
	cat $^ > $@

handlebars/teoremer_handlebars.js:
	${MAKE} -C handlebars

clean:
	${MAKE} -C handlebars clean

