FROM debian:jessie

RUN apt-get update \
  && apt-get clean \
  && apt-get install -y \
        curl \
        python3 \
        python3-pip \
  && rm -rf /var/lib/apt/lists/* \
  && pip3 install -U pip \
  && ln -s /usr/bin/python3 /usr/bin/python

RUN mkdir /nodejs \
  && curl -s https://nodejs.org/dist/v6.9.2/node-v6.9.2-linux-x64.tar.gz | tar xvzf - -C /nodejs --strip-components=1

ENV PATH $PATH:/nodejs/bin
