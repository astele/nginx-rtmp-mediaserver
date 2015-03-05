#!/bin/bash

cd /host_www/media/rec
/usr/bin/find . -name '*.mp4' -mmin -60 -exec /bin/bash -c '/usr/local/bin/avconv -i $1 -r 1 -vframes 1 -s 128x96 -b:v 512k -f image2 ../img/${1//\.mp4/}.jpg' _ {} \;

