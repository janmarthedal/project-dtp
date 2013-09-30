cd ../..
rm -rf production
mkdir production
cd production
cp -r ../analysis .
cp -r ../api .
cp -r ../document .
cp -r ../drafts .
cp -r ../items .
cp -r ../main .
cp -r ../media .
cp -r ../sources .
cp -r ../tags .
cp -r ../templates .
cp -r ../thrms .
cp -r ../users .
cp ../manage.py .
mkdir log
find . -name '*.pyc' -exec rm {} \;
find . -name '.gitignore' -exec rm {} \;

cd templates
TMP=`git show -s --format="%ci" HEAD | sed 's/^\(....\)-\(..\)-\(..\).*/\1.\2.\3/'`.`git rev-parse --short HEAD`; sed -i "s/COMMITDATA/$TMP/" base.html
cd .. 

cd main/static
cat css/*.css > teoremer.css
uglifyjs js/teoremer.js js/templates.js -o teoremer.js -c -m
rm -rf css
rm -rf js
cd ../..

tar cjf ../production.tar.bz2 *
