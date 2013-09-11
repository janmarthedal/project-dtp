find .. -path ../virtualenv -prune -or -name '*.py' -or -name '*.html' | xargs sed -i 's/[ \t]*$//'
find ../src -name '*.handlebars' -or -name '*.js' | xargs sed -i 's/[ \t]*$//'
