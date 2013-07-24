find .. -name '*.py' -or -name '*.html' | xargs sed -i 's/[ \t]*$//'
