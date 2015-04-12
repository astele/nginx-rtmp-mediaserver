#!/usr/bin/env bash

# "timeout" for OS X (from https://gist.github.com/jaytaylor/6527607)
function timeout() { perl -e 'alarm shift; exec @ARGV' "$@"; }

st=0;
while [ $st -lt 6 ];
do
    sleep 10;
    for c in rptcam1.dtdns.net:554
    do
        echo $c;
        ( timeout 1 bash -c 'cat < /dev/null > /dev/tcp/'${c/:/\/}; ) && echo Ok || echo No;
#       or
#       ( timeout 2 bash -c "exec 2>/dev/null; echo -en > `echo /dev/tcp/$c | sed -e 's/:/\//'`") && echo OK || `pkill -f $c`;
    done
    st=$((st+1));
done