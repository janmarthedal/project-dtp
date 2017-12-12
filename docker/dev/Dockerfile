FROM python:3.6.2

RUN mkdir /nodejs \
  && curl -s https://nodejs.org/dist/v9.2.1/node-v9.2.1-linux-x64.tar.gz | tar xvzf - -C /nodejs --strip-components=1

ENV PATH $PATH:/nodejs/bin
