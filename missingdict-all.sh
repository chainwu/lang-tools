#!/bin/bash 

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <dir>"
    exit -1
fi

ALLWAV=`ls $1/*.txt`

for ii in $ALLWAV;
do
    i=${ii//\//\\\\}
    #i=`echo $$i|sed 's/\\/\//g'`
    echo $i
    txtfile="${i::-4}".txt
    pushd . > /dev/null
    echo python3 MissingDict.py $txtfile
    #python3 MissingDict.py $txtfile
    popd > /dev/null
done
