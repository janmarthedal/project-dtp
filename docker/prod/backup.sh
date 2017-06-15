cd /tmp
rm -rf mathitems-backup
mkdir mathitems-backup
cd mathitems-backup
mkdir media

docker exec prod_app_1 python manage.py medialist | while read name
do
   docker cp prod_app_1:/code/media-files/$name media/$name
done

docker exec prod_app_1 python manage.py backup > data.json

out=/tmp/mathitems-`date -u +%Y%m%d%H%M%S`.tar.bz2

tar cjf "$out" *

cd ..
rm -rf mathitems-backup

echo "$out"
