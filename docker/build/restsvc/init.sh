#!/bin/bash
INDEX="/usr/share/nginx/html/index.html"
echo "<pre>" > $INDEX
env >> $INDEX
echo "</pre>" >> $INDEX

nginx -g "daemon off;"
