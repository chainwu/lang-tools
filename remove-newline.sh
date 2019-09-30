#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file>"
    exit -1
fi

sed ':a;N;$!ba;s/\n/ /g' $1
