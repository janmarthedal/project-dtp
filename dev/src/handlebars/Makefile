templates := $(patsubst %.handlebars,../../../static/js/%.js,$(wildcard *.handlebars))

all: $(templates)

../../../static/js/%.js: %.handlebars
	handlebars $< -k each -k if -k foreach -n "teoremer.templates" -f $@

clean:
	rm -f $(templates)

.PHONY: all clean
