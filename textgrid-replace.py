#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
""" Usage:
      textgrid-replace textgridfile tradition_pos_file
"""

import sys
import tgt

def textgrid_replace(txtgrid, tradchin):
    #first read textgrid file
    tg = tgt.io.read_textgrid(txtgrid)
    tiernames = tg.get_tier_names()
    lowertiernames = [x.lower() for x in tiernames]
    print(tiernames)
    print(lowertiernames) 

    if any('word' in s for s in lowertiernames):
        trn = [x for x in tiernames if 'word' in x.lower()]
        wtiername = trn[0]
        wtier = tg.get_tier_by_name(wtiername)
        print(wtier)

        cnt = 0
        for o in wtier._objects:
            if o.text != 'sp':
                cnt = cnt+1
        print(cnt)
    else:
        print("Cannot find tier with name 'word'")
        exit(-1)

    #then read traditional chinese pos file
    with open(tradchin) as f:
        lineList = f.read().splitlines()

    trll = []
    for i in lineList:
        trll.append(i.split())

    trl = [val for sublist in trll for val in sublist]
    print(trl)
    print(len(trl))


    if len(trl) == cnt:
        tridx = 0
        for o in wtier._objects:
            if o.text != 'sp':
                o.text = trl[tridx]
                tridx = tridx + 1
        print(wtier)
        tgt.io.write_to_file(tg, txtgrid+'.reptxt', format="long")
    else:
        print("Textgrid tier does not match with the text")
        exit(-1)

if __name__ == '__main__':
    try:
        # get the three mandatory arguments
        txtgrid = sys.argv[1]
        tradchin = sys.argv[2]
    except:
        print(__doc__)
        sys.exit(0)

textgrid_replace(txtgrid, tradchin)
