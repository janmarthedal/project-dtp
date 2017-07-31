FROM node:6.11.1

WORKDIR /code

COPY . .

RUN npm install \
  && npm run build

CMD node dst/server.js
