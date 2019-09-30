#!/bin/bash 

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file>"
    exit -1
fi

recode -f UTF-8..BIG-5 $1
./CKIPWSTester ws.ini $1 $1.tag
recode -f UTF-16LE..UTF-8 $1.tag
../lang-tools/paren-process.sh $1.tag
