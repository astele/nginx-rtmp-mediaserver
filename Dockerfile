FROM python:2.7.8-onbuild
MAINTAINER Andrey Filippov (https://github.com/astele)
ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true
ADD . /src
WORKDIR /src