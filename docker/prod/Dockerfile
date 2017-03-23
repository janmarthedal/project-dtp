FROM py3node

# https://github.com/nginxinc/docker-nginx/blob/master/mainline/jessie/Dockerfile

ENV NGINX_VERSION 1.11.10-1~jessie

RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62 \
	&& echo "deb http://nginx.org/packages/mainline/debian/ jessie nginx" >> /etc/apt/sources.list \
	&& apt-get update \
	&& apt-get install --no-install-recommends --no-install-suggests -y \
						ca-certificates \
						nginx=${NGINX_VERSION} \
						gettext-base \
                        libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uwsgi mysqlclient \
    && rm /etc/nginx/conf.d/* /var/log/nginx/* \
    && sed -i 's/^user .*/user www-data;/' /etc/nginx/nginx.conf

WORKDIR /code

COPY . .

RUN cp docker/prod/dtp.conf /etc/nginx/conf.d/ \
    && sed -i 's/^DEBUG *=.*/DEBUG = False/' project/settings.py \
    && pip install -r requirements.txt \
    && npm install \
    && python manage.py collectstatic --noinput \
    && chown -R www-data:www-data .

# forward request and error logs to docker log collector
#RUN ln -sf /dev/stdout /var/log/nginx/access.log \
#	&& ln -sf /dev/stderr /var/log/nginx/error.log

EXPOSE 80 443

CMD uwsgi --uid www-data --daemonize /var/log/uwsgi.log --socket app.sock --module project.wsgi \
    && nginx -g "daemon off;"
