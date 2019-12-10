#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <dir>"
    exit -1
fi

ALLWAV=`ls $1/*.wav`

for ii in $ALLWAV;
do
    i=${ii//\//\\\\}
    #i=`echo $$i|sed 's/\\/\//g'`
    echo $i
    txtfile=${i::-4}.brk
    txtgrid=${i::-4}.textgrid
    pushd . > /dev/null
    echo python3 Calign.py $i $txtfile $txtgrid
    python3 Calign.py $i $txtfile $txtgrid
    popd > /dev/null
done
