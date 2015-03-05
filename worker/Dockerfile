FROM python:2.7.8-onbuild
MAINTAINER Andrey Filippov (https://github.com/astele)
ENV PYTHONUNBUFFERED 1
ENV C_FORCE_ROOT true
RUN apt-get -q -y update \
    && apt-get -q -y install apt-utils make build-essential libssl-dev \
        zlib1g-dev libpcre3 libpcre3-dev libmp3lame-dev libsdl1.2-dev curl pgp yasm \
    && apt-get -q -y install libx264-dev \
    && apt-get -q -y clean && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*
RUN cd /root \
    && curl -L http://downloads.sourceforge.net/project/opencore-amr/fdk-aac/fdk-aac-0.1.3.tar.gz > fdk-aac.tgz \
    && mkdir fdk-aac && tar xzf fdk-aac.tgz -C fdk-aac --strip 1 && cd fdk-aac \
    && ./configure && make install
RUN cd /root && curl -L -O https://libav.org/releases/libav-11.2.tar.gz \
    && mkdir libav && tar xzf libav-11.2.tar.gz -C libav --strip 1 && cd libav \
    && ./configure --enable-gpl --enable-nonfree \
        --enable-libfdk-aac --enable-libx264 \
    && make install
RUN apt-get -q -y autoremove
RUN ldconfig
ADD . /src
WORKDIR /src