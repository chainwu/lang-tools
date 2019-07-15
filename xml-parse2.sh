#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <file>"
    exit -1
fi

xmllint --xpath "string(//text)" $1 |sed "s/，\|「\|」\|。\|：\|．\|；\|？\|！\|—\|【\|】\|《\|》\|"+vrv"\|"+vrr"\|"+spo"\|"+spv"\|（\|）\|\[\|\]\|、\|,\|\.\|:\|;\|\?\|\!\|\"\|\%\|'∥'//g"| sed -e "s/(/ /g" | sed -e "s/)/\n/g" | sed -e 's/COLONCATEGORY\|PAUSECATEGORY\|PERIODCATEGORY\|PARENTHESISCATEGORY\|QUESTIONCATEGORY\|COMMACATEGORY\|EXCLANATIONCATEGORY\|SEMICOLONCATEGORY\|DASHCATEGORY\|SPCHANGECATEGORY//g' | sed -e 's/^[ 　\t]*//' | sed -e '/^$/d'




#xmllint --xpath "string(//text)" $1 |sed "s/，\|。\|：\|；\|？\|！\|（\|）\|、\|,\|\.\|:\|;\|\?\|\!\|\"\|\%\-//g"|sed -e 's/(COLONCATEGORY)\|(PAUSECATEGORY)\|(PERIODCATEGORY)\|(PARENTHESISCATEGORY)\|(QUESTIONCATEGORY)\|(COMMACATEGORY)\|(EXCLANATIONCATEGORY)\|(SEMICOLONCATEGORY)\|(DASHCATEGORY)\|(SPCHANGECATEGORY)//g'|perl -ne 'printf "%s\n", join(" " , $_ =~ /["(].*?[)"]/g)'|sed -e 's/(//g'|sed -e 's/)//g'|sed '/^$/d'> t2.txt

#paste -d '\n' t1.txt t2.txt

#rm t1.txt t2.txt
