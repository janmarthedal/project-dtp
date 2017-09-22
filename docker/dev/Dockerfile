FROM python:3.6.2

RUN mkdir /nodejs \
  && curl -s https://nodejs.org/dist/v6.11.3/node-v6.11.3-linux-x64.tar.gz | tar xvzf - -C /nodejs --strip-components=1

ENV PATH $PATH:/nodejs/bin
