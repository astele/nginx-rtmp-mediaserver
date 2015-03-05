#!/bin/bash

/usr/bin/find /host_www/media -name '*.flv' -mmin +60 -print -exec /bin/rm '{}' \;

