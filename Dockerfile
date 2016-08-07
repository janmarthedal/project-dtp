FROM nginx

RUN apt-get update \
  && apt-get install -y python3 python3-pip \
  && rm -rf /var/lib/apt/lists/* \
  && pip3 install uwsgi \
  && rm /etc/nginx/conf.d/* /var/log/nginx/* \
  && sed -i 's/^user .*/user www-data;/' /etc/nginx/nginx.conf

WORKDIR /code

COPY . .

RUN pip3 install -r requirements.txt \
  && cp docker/dtp.conf /etc/nginx/conf.d/ \
  && chown -R www-data:www-data .

CMD uwsgi --uid www-data --daemonize /var/log/uwsgi.log --socket app.sock --module project.wsgi && nginx -g "daemon off;"
