#!/usr/bin/env python
# coding: utf-8
""" Usage:
    python3 textfrid_layer.py directory
    
    This file takes a directory, process all .textgrid file and output output 12-tier txtgrid file
    directory: the directory that want to processed
    
    The output is textgrid_file+".12"
"""

from __future__ import print_function, division

import pandas as pd
#讀入 EHowNet
from ehownet_python3 import *

def read_databases():
    try:
        #讀入字典
        cdict = pd.read_csv('cdict_cond.csv')
        #cdict.drop_duplicates(subset = None, keep = "last", inplace = True)
        #print(dict)
        
        EHowTree=EHowNetTree("db/ehownet_ontology.sqlite")
        #tree=EHowNetTree("db/ehownet_ontology_sim.sqlite")
        #print(dict)
    
        # 讀入 SAMPA 
        sampadict = pd.read_excel('sampa_revised.xls')
        #print(sampadict)
        return(cdict, EHowTree, sampadict)
    except Exception as e:
        print(e)
        exit(-1)


# In[2]:


import os
import sys
import tgt

EXTENSION = 'TextGrid'

def print_tiernames(filenames):
    for filename in filenames:
        try:
            tg = tgt.io.read_textgrid(filename)
            print(filename)
            for tiername in tg.get_tier_names():
                print('\t' + tiername)
        except err:
            print(filename + ' caused a problem.')
            sys.stderr.write('ERROR: %s\n' % str(err))

def read_txtgrid(filename):
    tg = tgt.io.read_textgrid(filename)
    return tg

def add_text_tier(tg, NNM=""):
    new_tier = tgt.core.PointTier(name=NNM)
    tg.add_tier(new_tier)
    return new_tier

def add_interval_tier(tg, NNM="", STT=0, ETT=0):
    new_tier = tgt.core.IntervalTier(name=NNM, start_time = STT, end_time = ETT)
    tg.add_tier(new_tier)
    return new_tier

def print_tier(tg):
    for tiername in tg.get_tier_names():
        print('\t' + tiername)   

def write_txtgrid(tg, NNM):
    tgt.io.write_to_file(tg, filename=NNM )
    
def remove_old_tier(tg, name):
    if (tg.has_tier(name)):
        tg.delete_tier(name)


# In[3]:


import numpy as np
import math

def remove_noises(tr):
    for o in tr._objects:
        if o.duration() < 0.01:
            tr.delete_annotation_by_start_time(o.start_time)

def filling_gaps(tr):
    tr.start_time = 0
    o = tr._objects[0]
    if o.start_time != 0:
        o.start_time = 0
    o = tr._objects[-1]
    if o.end_time != tr.end_time:
        o.end_time = tr.end_time
    #print(tr)
    idx = len(tr._objects)
    for i in range(1,idx):
        if tr._objects[i].start_time != tr._objects[i-1].end_time:
            tr._objects[i].start_time = tr._objects[i-1].end_time

def align_tiers(wtr, ptr):
    for w in wtr._objects:
        wst = w.start_time
        wet = w.end_time
        pann = ptr.get_annotations_between_timepoints(w.start_time, w.end_time, False, False)
 
        if len(pann) != 0:
            if not math.isclose(wst, pann[0].start_time):
                pann2 = ptr.get_annotations_between_timepoints(w.start_time, w.end_time, True, False)
                pst1 = pann[0].start_time
                pst2 = pann2[0].start_time
                #print("S:", w.start_time, pann[0].start_time, pann2[0].start_time)
                if abs(wst - pst1) < abs(wst - pst2):
                    pann[0].start_time = wst
                else:
                    pann2[0].start_time = wst

            #print("Wet:", math.isclose(wet, pann[-1].end_time), wet, pann[-1].end_time)
            if  not math.isclose(wet, pann[-1].end_time):
                pann2 = ptr.get_annotations_between_timepoints(w.start_time, w.end_time, False, True)
                pet1 = pann[-1].end_time
                pet2 = pann2[-1].end_time
                #print("E: ", wet, pann[-1].end_time, pann2[-1].end_time)
                if abs(wet - pet1) < abs(wet - pet2):
                    pann[-1].end_time = wet
                else:
                    pann2[-1].end_time = wet


# In[4]:


def contains_chinese(check_str):
    """
    判断字符串中是否包含中文
    :param check_str: {str} 需要检测的字符串
    :return: {bool} 包含返回True， 不包含返回False
    """

    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True

    return False

# In[5]:


# Major program starts here

(cdict, EHowTree, sampadict) = read_databases()
#file_translation("step1.TextGrid")


# In[6]:


# Extract all tha annotations from word layer
# 處理第一層中文層

def chinese_tier(wordtier, phonetier):
    annlist = []
    et = wordtier.end_time
    st = wordtier.start_time
    
    for ann in wordtier._objects:
        if ann.text != 'sp' and ann.text != "" : 
            annlist.append(ann)

    #print(annlist)

    ctext = ""

    for a in annlist:
        atext = a.text.replace("~","")
        atext = atext.replace("^","") 
        atext = atext.replace(" ","")
        if (contains_chinese(atext)):
            ctext = ctext + atext
            # print(a.text)
        else:
            ctext = ctext + " " + atext + " "

    #print(ctext)
    #ctext = ctext.replace('~', '')
    #ctext = ctext.replace('^', '')
    ctier = tgt.core.IntervalTier(st, et, u"IU")
    cann = tgt.core.Annotation(st,et, ctext)
    ctier.add_annotation(cann)
    #print(ctext)
    
    return (ctier, ctext)


# In[7]:


# 處理第二 層英文層

from googletrans import Translator
import time

def english_tier(wordtier, phonetier, ctext):
    time.sleep(2)
    et = wordtier.end_time
    st = wordtier.start_time
    
    translator = Translator()
    tr = translator.translate(ctext, dest = 'en')
    print (tr.text)

    etier = tgt.core.IntervalTier(st, et, "English")
    #add_text_tier(newtg, "English")
    eann = tgt.core.Annotation(st, et,tr.text)
    etier.add_annotation(eann)
    return etier


# In[8]:

def new_word_tier(wordtier, phonetier):
    et = wordtier.end_time
    st = wordtier.start_time
    
    newtier = tgt.core.IntervalTier(st, et, "Word")
    for ann in wordtier._objects:
        newtext = ann.text.replace('~','').replace('^','')
        newann = tgt.core.Annotation(ann.start_time, ann.end_time, text=newtext)
        newtier.add_annotation(newann)
    return newtier

# 處理第三層 加入詞意層

def pos_tier(wordtier, phonetier):
    et = wordtier.end_time
    st = wordtier.start_time
    postier = tgt.core.IntervalTier(st, et, "Word")

    for ann in wordtier._objects: 
        newann = tgt.core.Annotation(ann.start_time, ann.end_time, text=" ")
        anntext = ann.text.replace("~","")
        anntext = anntext.replace("^","")
        anntext = anntext.replace(" ","")
        if (contains_chinese(anntext)): 
            newannstr = ""
            #去 EHowNet 查詞性
            posp=EHowTree.searchWord(anntext)
            print(anntext, posp)
            if posp:
                for w in posp:
                    #print(w.pos)
                    newannstr = newannstr + w.pos + " "
                #print(node)
                newann.text = newannstr.rstrip()
        elif anntext == 'sp':
            newann.text = 'sp'
            #print(newannstr)
            #print(c, "[", newann.start_time, newann.end_time, "]", ss)
        postier.add_annotation(newann)

    print(postier)
    return(postier)


# In[9]:


def is_sampa_notation(sampa, text):
    sz = sampa[sampa['SAMPA'] == text].size
    return sz != 0

def get_ipa(sampa, note1, note2, note3):
    """get_ipa takes SAMPA dictionary and 3 consecutive notations, and return an IPA Note list to be replaced, 
       for example, when given SAMPA note1, note2, note3
             ('m', DONTCARE, DONTCARE), it will return [m, None, None]
             when given 
             ('W', '@', 'n'), it will return ['ɥ', 'ɛ', 'n']
             
             if the result contains "_", it means that the two SAMPA notes needs to be merged into one IPA note
    """
    if note1 not in ['@', 'W', 'y', '&', 'w']:
        return [sampa.loc[sampa['SAMPA'] == note1]['IPA'].to_string(index = False).strip(), None, None]
    elif note1 == '@':
        return ['a', None, None]
    elif note1 == 'W':
        if note2 == '@' and note3 == 'n':
            return ['ɥ', 'ɛ', 'n']
        else:
            return ['ɥ', None, None]
    elif note1 == 'y':
        if note2 == 'i' and note3 == 'n':
            return ['i', '_', 'n']
        else:
            return ['j', None, None]
    elif note1 == '&':
        if note2 == 'N':
            return ['ə', 'ŋ', None]
        elif note2 == 'n':
            return ['ə', 'n', None]
        else:
            return ['ɤ', None, None]
    elif note1 == 'w':
        if note2 == '&' and note3 == 'N':
            return ['w','o', 'ŋ']
        elif note2 == 'u':
            return ['u', "_", None]
        elif note2 == 'o':
            return ['ɔ', "_", None]
        elif note2 == '>':
            return ['w', 'ɔ', None]
        else:
            return ['w', None, None]
    
def get_result_len(x):
    if x[-2] == None:
        return 1
    elif x[-1] == None:
        return 2
    else:
        return 3

def ipa_tier(wordtier, phonetier):
    et = phonetier.end_time
    st = phonetier.start_time
    ipatier = tgt.core.IntervalTier(st, et, "IU/phone")

    wet = wordtier.end_time
    wst = wordtier.start_time
    tierlen = phonetier.__len__()
    
    for wann in wordtier._objects:
        annlist = phonetier.get_annotations_between_timepoints(wann.start_time, wann.end_time)
        tierlen = len(annlist)
        i = 0
        while i < tierlen :
            ann = annlist[i]
            print(i, ":", ann.text)

            if ann.text == "sp":
                newann = tgt.core.Annotation(ann.start_time, ann.end_time, 'sp')
                ipatier.add_annotation(newann)
                i = i + 1
                continue

            if not is_sampa_notation(sampadict, ann.text):
                newann = tgt.core.Annotation(ann.start_time, ann.end_time, "")
                i = i + 1
                continue
                
            if i < tierlen - 2:
                annplus1 = annlist[i+1]
                annplus2 = annlist[i+2]
                arg = ann.text
                arg1 = annplus1.text
                arg2 = annplus2.text
            elif i == tierlen - 2:
                annplus1 = annlist[i+1]
                arg = ann.text
                arg1 = annplus1.text
                arg2 = None
            else:
                arg = ann.text
                arg1 = None
                arg2 = None                
                
            resultlist = get_ipa(sampadict, arg, arg1, arg2)
            results_len = get_result_len(resultlist)
            print(resultlist)
            
            for j in range(len(resultlist)):
                if resultlist[j] == None:
                    continue
                if resultlist[j] == '_':
                    i = i + 1
                    newann = tgt.core.Annotation(prevann.start_time, annplus1.end_time, prevann.text)
                    ipatier.delete_annotation_by_start_time(prevann.start_time)
                    ipatier.add_annotation(newann)
                else:
                    ann = annlist[i]
                    newann = tgt.core.Annotation(ann.start_time, ann.end_time, resultlist[j])
                    i = i + 1
                    prevann = newann   
                    ipatier.add_annotation(newann)
     
    print(ipatier)
    return(ipatier)


# In[10]:


#處理第五層 IU/Syllable (CGVN)層
import itertools
cgvn_pattern=['V', 'VN', 'NV', 'CV', 'GV', 'VG', 'CGV', 'GVN', 'GVG', 'CVG', 'CVN', 'CGVG', 'CGVN']

def cgvn_split(cgvnstr, clist):
    if cgvnstr == "":
        clist.insert(0, "*")
        #print(clist)
        return True
    else:
        match = False
        for ptn in cgvn_pattern:
            #print("Testing pattern ", ptn, "with ", cgvnstr)
            if cgvnstr.startswith(ptn):
                if cgvn_split(cgvnstr[len(ptn):], clist):
                    clist.insert(0, ptn)
                    match = True
        return match

def get_cgvn(sampa, text):
    return sampa.loc[sampa['IPA2'] == text]['CGVN2'].to_string(index = False).strip()

def cgvn_tier(wordtier, phonetier):
    et = phonetier.end_time
    st = phonetier.start_time
    cgvntier = tgt.core.IntervalTier(st, et, "IU/syllable")
    cgvnstartier = tgt.core.IntervalTier(st, et, "IU/syllable/*")
    for ann in wordtier._objects:
        newann = tgt.core.Annotation(ann.start_time, ann.end_time, "")
        newstarann = tgt.core.Annotation(ann.start_time, ann.end_time, "")
        cgvnsplit=""
        if contains_chinese(ann.text):
            #詞含有中文，抓出音來
            pholist = phonetier.get_annotations_between_timepoints(ann.start_time, ann.end_time)
            #print(ann.text)
            cgvnstr = ''
            for p in pholist:
                cgvn = get_cgvn(sampadict, p.text)
                print(p.text, cgvn)
                cgvnstr = cgvnstr + cgvn
            clist=[]
            cgvn_split(cgvnstr, clist)
            splist = [list(y) for x, y in itertools.groupby(clist, lambda z: z == "*") if not x]
            if len(splist) != 1:
                cgvnsplit="*"
            cgvn=""
            for j in splist:
                listToStr = ' '.join([str(elem) for elem in j])
                cgvn = cgvn+listToStr+" | "
            cgvnstr=cgvn[:-3]
        elif ann.text == "sp":
            cgvnstr = "sp"
        else:
            cgvnstr = ""
        
        newann.text = cgvnstr
        newstarann.text=cgvnsplit
        cgvntier.add_annotation(newann)
        cgvnstartier.add_annotation(newstarann)
    
    return (cgvntier, cgvnstartier)

#cgvn_tier(wordtier, phonetier)


# In[11]:


#第六層處理四聲層
def is_in_dict(cdict, text):
    sz = cdict[cdict['word'] == text].size
    return sz != 0

def get_phone(cdict, text):
    answer = cdict[cdict['word'] == text]['phone']
    if answer.size == 0:
        return " "
    elif answer.size == 1:
        return answer.to_string(index = False)
    else:
        anslist= answer.to_string(index = False).split()
        return anslist[0]

def foursounds(c):
    if 'ˋ' in c:
        return "51 "
    elif 'ˊ' in c:
        return "35 "
    elif 'ˇ' in c:
        return "21 "
    elif '˙' in c:
        return "0 "
    else:
        return "55 "
    
def to_tone(phone):
    tone = ""
    phlist = phone.split()
    for p in phlist:
        #print(p)
        tone = tone + foursounds(p)
    return tone

def tone_tier(wordtier, phonetier):
    et = phonetier.end_time
    st = phonetier.start_time    
    to1tier = tgt.core.IntervalTier(st, et,"IU/tone")

    for ann in wordtier._objects:
        newann = tgt.core.Annotation(ann.start_time, ann.end_time, text="")
        xanntext = ann.text.replace('~','').replace('^','').replace(' ','')
        if (contains_chinese(xanntext)):
            if is_in_dict(cdict, xanntext):
                phone = get_phone(cdict, xanntext)
                newann.text = to_tone(phone)
            else:
                print(xanntext, "IS NOT in DICT") 
                p = ''
                for c in xanntext:
                    phone = get_phone(cdict, c) 
                    p = p + to_tone(phone)
                newann.text = p
            print(xanntext, phone, newann.text)

        elif ann.text == "sp":
            newann.text = "sp"

        to1tier.add_annotation(newann)

    print(to1tier)
    return to1tier

#第八層 copy word tier 然後把所有字拿掉
def eutype_tier(wordtier, phonetier):
    et = phonetier.end_time
    st = phonetier.start_time    
    eutier = tgt.core.IntervalTier(st, et, "EU/Type")
    
    for ann in wordtier._objects:
        if '~' in ann.text:
            newann = tgt.core.Annotation(ann.start_time, ann.end_time, '~')
        elif '^' in ann.text :
            newann = tgt.core.Annotation(ann.start_time, ann.end_time, '^')
        else:
            newann = tgt.core.Annotation(ann.start_time, ann.end_time, '')
        eutier.add_annotation(newann)
        
    print(eutier)
    return eutier

def subject_tier(wordtier, phonetier):
    et = phonetier.end_time
    st = phonetier.start_time    
    subjtier = tgt.core.IntervalTier(st, et, "Subject")
	
    newann = tgt.core.Annotation(st, et, '#001AM_N')
    subjtier.add_annotation(newann)
    print(subjtier)
    return subjtier
	
# In[12]:


# Two tiers from original textgrid file
import copy
import glob

def textgrid_main(txtgridr):
    print(txtgridr)
    txtlist = glob.glob(txtgridr+"/*.TextGrid")
    print("File list", txtlist)
    for txtgridf in txtlist:
        print("Processing", txtgridf)
        tg = read_txtgrid(txtgridf)
        ophonetier = tg.get_tier_by_name('phone')
        owordtier =  tg.get_tier_by_name('word')

        sampatier = ophonetier.get_copy_with_gaps_filled()
        sampatier.name = "IU/SAMPA"
		
        phonetier = ophonetier.get_copy_with_gaps_filled()
		
        wordtier  = owordtier.get_copy_with_gaps_filled()
        wordtier.name="Word"

        remove_noises(phonetier)
        remove_noises(wordtier)

        filling_gaps(phonetier)
        filling_gaps(wordtier)

        align_tiers(wordtier, phonetier)

        st = wordtier.start_time
        et = wordtier.end_time

        newtg = tgt.core.TextGrid()

        (ctier, ctext) = chinese_tier(wordtier, phonetier)
        etier = english_tier(wordtier, phonetier, ctext)
        postier = pos_tier(wordtier, phonetier)
        nwordtier = new_word_tier(wordtier, phonetier)
        ipatier = ipa_tier(wordtier, phonetier)
        (icgtier, cgstartier) = cgvn_tier(wordtier, ipatier)
        ecgtier = icgtier.get_copy_with_gaps_filled()
        ecgtier.name = "EU/syllable"
		
        euphonetier = copy.deepcopy(ipatier)
        euphonetier.name = "EU/phone"		
        
        ttier = tone_tier(nwordtier, phonetier)
        typetier = eutype_tier(wordtier, phonetier)
        #newtg.add_tier(typetier)

        subjecttier = subject_tier(wordtier, phonetier)
        #newtg.add_tier(subjecttier)

        # Construct contents

	#tier 1 Chinese tier
        newtg.add_tier(ctier)
		
	#tier 2 English tier
        newtg.add_tier(etier)
		
	# Tier 3 new word tier
        newtg.add_tier(owordtier)
        newtg.add_tier(postier)
        
	# Tier 4 IU/SAMPA tier
        newtg.add_tier(sampatier)
		
	# Tier 5 phone tier
        newtg.add_tier(ipatier)	

	#Tier 6 IU/syllable (CGVN) tier 
        newtg.add_tier(icgtier)
        newtg.add_tier(cgstartier)
        
	#Tier 7 IU/tone tier
        newtg.add_tier(ttier)
		
	#Tier 8 EU/phone tier
        newtg.add_tier(euphonetier)
		
	#Tier 9 EU/tone (syllable) tier
        newtg.add_tier(ecgtier)
		
	#Tier 10 EU/tone tier
        ettier = ttier.get_copy_with_gaps_filled()
        ettier.name="EU/tone"
        newtg.add_tier(ettier)
		
	#Tier 11: EU/type type tier
        newtg.add_tier(typetier)
		
	#Tier 12: Subject Tier
        newtg.add_tier(subjecttier)

        write_txtgrid(newtg, txtgridf+".12")

# In[13]:


import sys

def main():
    if (len(sys.argv) != 2):
        print(__doc__)
        sys.exit(-1)
    else:
        txtgridr = sys.argv[1]
        textgrid_main(txtgridr)
        
if __name__ == "__main__":
    main()

