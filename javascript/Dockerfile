FROM node:6.10.2

WORKDIR /code

COPY . .

RUN npm install -g gulp-cli \
  && npm install \
  && gulp

CMD node dst/server.js
