#!/bin/bash

ALLWAV=`ls *.wav`
#echo $ALLWAV

mkdir -p bak
mv *.wav bak
ALLWAV=`ls bak/*.wav`
for w in $ALLWAV
do
    echo Spliting $w ..
    NEWWAV=`basename -s .wav $w`
    NEWSUFFIX=_.wav
    sox $w $NEWWAV$NEWSUFFIX trim 0 30 : newfile restart
done

mkdir -p bakrate
mv *.wav bakrate
NEWWAV=`ls bakrate/*.wav`
for nw in $NEWWAV
do
     echo Bitrate convertsion $nw..
     CONVF=`basename -s .wav $nw`
     sox $nw -b 16 $CONVF.wav
done

rm -rf bakrate
