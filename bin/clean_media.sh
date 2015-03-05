#!/bin/bash

/usr/bin/find /host_www/media -regex '.*?_\(2[1-3]\|0[0-7]\):00\.\w+?' -print -exec /bin/rm '{}' \;
/usr/bin/find /host_www/media -type f -mtime +30 -print -exec /bin/rm '{}' \;

