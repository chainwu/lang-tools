#!/usr/bin/env python3
#-*- coding: utf-8 -*-
""" Usage:
    python3 MissingDict.py textfile
    This program will filter the words in Yuan's Forced alignment dictionary 
    and try to break the missing term into single character so that the FA 
    can performed better. The input textfile must be in simplifed Chinese 
    UTF-8 encoding.

    It will generate the following files, 
       txtfile.brk: The break down files
       txtfile.dict: The standalone dictionary file can be used by forced 
       alignment
       txtfile.mss: The missing word even after break down.
"""

import sys
import os

DICT='dict'

def is_ascii(check_str):
     return all(ord(c) < 128 for c in check_str)

def contains_chinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串,
    :return: {bool} 包含返回True， 不包含返回False
    """
    for ch in check_str:
        if u'\\u4e00' <= ch <= u'\\u9fff':
            return True
    return False

def missing_main(txtfile):
    # Read dict for standalone dict process
    ddict = dict()
    df = open(DICT)
    for line in df:
        li = line.replace('\n', '')
        li1 = li.split(" ",1)
        if len(li1) > 1:
            li1[1] = li1[1].strip().rstrip()
            #print(li1)
            ddict.setdefault(li1[0], [])
            ddict[li1[0]].append(li1[1])
    #print(ddict)
    df.close()

    # Read dict for string matching
    dictlist = []
    df = open(DICT)
    for line in df:
        li1 = line.replace('\n', '')
        if li1 != '':
            li=li1.split()
            dictlist.append(li[0])
    list(set(dictlist))
    #print(dictlist)
    df.close()

    base = os.path.splitext(txtfile)[0]
    newtxtfile=base+'.brk'
    newmssfile=base+'.mss'
    newdictfile=base+'.dict'
    #print(newtxtfile, newmssfile, newdictfile)
    newtxt = open(newtxtfile, 'w')
    newmss = open(newmssfile, 'w')
    newdict = open(newdictfile, 'w')
    
    # Read the text file (CKIP output)
    for line in open(txtfile):
        li1 = line.replace('\n', '')

        #if the line is empty, skip
        if li1 == '':
            continue

        #for every term in the .txt file
        li=li1.split()
        for t in li:
            if t in dictlist:
                #In dict
                newtxt.write(t)
                newtxt.write(" ")

                for tt in ddict[t]:
                    newdict.write(t)
                    newdict.write("  ")
                    newdict.write(tt)
                    newdict.write("\n")
            else:
                #Not in dict
                if not is_ascii(t):
                    for i in range(len(t)):
                        newtxt.write(t[i])
                        newtxt.write(" ")
                        if t[i] in ddict:
                            for tt in ddict[t[i]]:
                                newdict.write(t[i])
                                newdict.write("  ")
                                newdict.write(tt)
                                newdict.write("\n")
                        else:
                            newmss.write("Missing: ")
                            newmss.write(t[i])
                            newmss.write("\n")
                else:
                    # Englist, definitely not in dict
                    newmss.write("Missing: ")
                    newmss.write(t)
                    newmss.write("\n")

        #newtxt.write("\n")

        
def print_usage():
    print(__doc__)
    sys.exit(0)

if __name__ == '__main__':
    try:
        txtfile = sys.argv[1]
        #print(txtfile)
        missing_main(txtfile)
    except Exception as e:
        print(e)
        print_usage()
        sys.exit(-1)

