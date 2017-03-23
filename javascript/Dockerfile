FROM debian:jessie

RUN apt-get update \
  && apt-get install -y curl \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir /nodejs \
  && curl -s https://nodejs.org/dist/v6.10.1/node-v6.10.1-linux-x64.tar.gz | tar xvzf - -C /nodejs --strip-components=1

ENV PATH $PATH:/nodejs/bin

WORKDIR /code

COPY . .

RUN npm install -g gulp-cli \
  && npm install \
  && gulp

CMD node dst/server.js
