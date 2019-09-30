#!/bin/bash 

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file>"
    exit -1
fi

nosuffix=`basename $1 .pos`
awk -v RS="[*]" -v AFN="$nosuffix" '{ print $0 > sprintf("%s_%03d.trad",AFN,NR) }' $1

SUBFILE=`ls $nosuffix_*.trad`

for f in $SUBFILE ;
do
    txtfn=`basename $f .trad`
    sed '/^[[:space:]]*$/d' $f > $f.tmp
    python3 -m opencc -c t2s -i $f.tmp -o $txtfn.txt
done
rm *.tmp
