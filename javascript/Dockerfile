FROM node:9.2.1

WORKDIR /code

COPY . .

RUN npm install \
  && npm run build

CMD node dst/server.js
