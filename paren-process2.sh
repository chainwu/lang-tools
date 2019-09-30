#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file>"
    exit -1
fi

cat $1 | sed '1s/^\xEF\xBB\xBF//'| sed -e "s/\r\n$/\n/" | sed -e 's/(COLONCATEGORY)\|(PAUSECATEGORY)\|(PERIODCATEGORY)\|(PARENTHESISCATEGORY)\|(QUESTIONCATEGORY)\|(COMMACATEGORY)\|(EXCLANATIONCATEGORY)\|(SEMICOLONCATEGORY)\|(DASHCATEGORY)\|(SPCHANGECATEGORY)//g' | sed "s/[(][^)]*[)]/()/g" |sed "s/()//g" | sed "s/-\|，\|「\|」\|。\|•\|：\|．\|；\|？\|！\|—\|【\|】\|《\|》\|"+vrv"\|"+vrr"\|"+spo"\|"+spv"\|（\|）\|\[\|\]\|、\|,\|\.\|:\|;\|\?\|\!\|\"\|\%\|'∥'//g" | sed -e "s/^[ 　\t]*//" | sed -e "s/\r//g"| sed -e '/^$/N;/^\n$/D'|sed 's/　/ /g'| sed 's/ /\n/g'
