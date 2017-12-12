FROM python:3.6.2

RUN mkdir /nodejs \
  && curl -s https://nodejs.org/dist/v9.2.1/node-v9.2.1-linux-x64.tar.gz | tar xvzf - -C /nodejs --strip-components=1

ENV PATH $PATH:/nodejs/bin

# https://github.com/nginxinc/docker-nginx/blob/master/mainline/jessie/Dockerfile

ENV NGINX_VERSION 1.11.13-1~jessie

RUN set -e; \
	NGINX_GPGKEY=573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62; \
	found=''; \
	for server in \
		ha.pool.sks-keyservers.net \
		hkp://keyserver.ubuntu.com:80 \
		hkp://p80.pool.sks-keyservers.net:80 \
		pgp.mit.edu \
	; do \
		echo "Fetching GPG key $NGINX_GPGKEY from $server"; \
		apt-key adv --keyserver "$server" --keyserver-options timeout=10 --recv-keys "$NGINX_GPGKEY" && found=yes && break; \
	done; \
	test -z "$found" && echo >&2 "error: failed to fetch GPG key $NGINX_GPGKEY" && exit 1; \
	exit 0

RUN echo "deb http://nginx.org/packages/mainline/debian/ jessie nginx" >> /etc/apt/sources.list \
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
