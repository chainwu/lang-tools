#!/bin/bash

MEDIAPATH=/var/www/html/textgrid
mkdir -p $(MEDIAPATH)
chown -R www-data.www-data $(MEDIAPATH)

