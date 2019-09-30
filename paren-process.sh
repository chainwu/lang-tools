#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file>"
    exit -1
fi

#ENCODING=`file -i examp.txt |awk '{print $3}'|sed 's/charset=//'`
#echo $ENCODING

#if [ $ENCODING != "UTF-8" ]; then
#    iconv -f BIG5 -t UTF-8 $1 > tmpfile.txt
#    PROCFILE=tmpfile.txt 
#else
#    PROCFILE=$1 
#fi

#echo $PROCFILE 
cat $1 | sed -e "s/\r\n$/\n/" | sed -e 's/(COLONCATEGORY)\|(PAUSECATEGORY)\|(PERIODCATEGORY)\|(PARENTHESISCATEGORY)\|(QUESTIONCATEGORY)\|(COMMACATEGORY)\|(EXCLANATIONCATEGORY)\|(SEMICOLONCATEGORY)\|(DASHCATEGORY)\|(SPCHANGECATEGORY)//g' | sed -e 's/[(][^)]*[)]//g' | sed "s/-\|，\|「\|」\|。\|•\|：\|．\|；\|？\|！\|—\|【\|】\|《\|》\|"+vrv"\|"+vrr"\|"+spo"\|"+spv"\|（\|）\|\[\|\]\|、\|,\|\.\|:\|;\|\?\|\!\|\"\|\%\|'∥'//g" | sed -e "s/^[ 　\t]*//" | sed -e "s/\r//g"| sed -e '/^$/N;/^\n$/D' |sed -e 's/　/ /g'
