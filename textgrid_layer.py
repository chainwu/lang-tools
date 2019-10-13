#!/usr/bin/env python
# coding: utf-8

# In[1]:


# 引用套件並縮寫為 pd  
import pandas as pd
#讀入 EHowNet
from ehownet_python3 import *

def read_databases():
    try:
        #讀入字典
        cdict = pd.read_excel('cdict_cond.xlsx')
        #cdict.drop_duplicates(subset = None, keep = "last", inplace = True)
        #print(dict)
        
        EHowTree=EHowNetTree("db/ehownet_ontology.sqlite")
        #tree=EHowNetTree("db/ehownet_ontology_sim.sqlite")
        #print(dict)
    
        # 讀入 SAMPA 
        sampadict = pd.read_excel('sampa_revised.xlsx')
        #print(sampadict)
        return(cdict, EHowTree, sampadict)
    except Exception as e:
        print(e)
        exit(-1)


# In[2]:


from __future__ import print_function, division
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
        if (contains_chinese(a.text)):
            ctext = ctext + a.text
            # print(a.text)
        else:
            ctext = ctext + " " + a.text + " "

    #print(ctext)
    ctier = tgt.core.IntervalTier(st, et, u"IU")
    cann = tgt.core.Annotation(st,et, ctext)
    ctier.add_annotation(cann)
    #print(ctext)
    
    return (ctier, ctext)


# In[7]:


# 處理第二層英文層

from googletrans import Translator

def english_tier(wordtier, phonetier, ctext):
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


# 處理第三層 加入詞意層

def pos_tier(wordtier, phonetier):
    et = wordtier.end_time
    st = wordtier.start_time
    postier = tgt.core.IntervalTier(st, et, "Word")

    for ann in wordtier._objects: 
        newann = tgt.core.Annotation(ann.start_time, ann.end_time, text=" ")
        if (contains_chinese(ann.text)): 
            newannstr = ""
            #去 EHowNet 查詞性
            posp=EHowTree.searchWord(ann.text)
            print(ann.text, posp)
            if posp:
                for w in posp:
                    #print(w.pos)
                    newannstr = newannstr + w.pos + " "
                #print(node)
                newann.text = newannstr.rstrip()
        elif ann.text == 'sp':
            newann.text = 'sp'
            #print(newannstr)
            #print(c, "[", newann.start_time, newann.end_time, "]", ss)
        postier.add_annotation(newann)

    print(postier)
    return(postier)


# In[9]:


def is_sampa_notation(sampa, text):
    sz = sampa[sampa['SAMPA'] == text].size
    if sz != 0 :
        return True
    else:
        return False

def get_ipa(sampa, text):
    return sampa.loc[sampa['SAMPA'] == text]['IPA'].to_string(index = False).strip()

def ipa_tier(wordtier, phonetier):
    et = phonetier.end_time
    st = phonetier.start_time
    ipatier = tgt.core.IntervalTier(st, et, "IPA")

    for ann in phonetier._objects:
        newann = tgt.core.Annotation(ann.start_time, ann.end_time, text=" ")
        if is_sampa_notation(sampadict, ann.text): 
            newann.text = get_ipa(sampadict, ann.text)
        elif ann.text == 'sp':
            newann.text = 'sp'
        ipatier.add_annotation(newann)

    print(ipatier)
    return(ipatier)


# In[10]:


#處理第五層 IU/Syllable (CGVN)層

def get_cgvn(sampa, text):
    return sampa.loc[sampa['SAMPA'] == text]['CGVN'].to_string(index = False).strip()

def cgvn_tier(wordtier, phonetier):
    et = phonetier.end_time
    st = phonetier.start_time
    cgvntier = tgt.core.IntervalTier(st, et, "EU/syllable")
    for ann in wordtier._objects:
        newann = tgt.core.Annotation(ann.start_time, ann.end_time, "")
        if contains_chinese(ann.text):
            #詞含有中文，抓出音來
            pholist = phonetier.get_annotations_between_timepoints(ann.start_time, ann.end_time)
            #print(ann.text)
            cgvnstr = ''
            for p in pholist:
                if is_sampa_notation(sampadict, p.text):
                    cgvn = get_cgvn(sampadict, p.text)
                    print(p.text, cgvn)
                    cgvnstr = cgvnstr + cgvn
        elif ann.text == "sp":
            cgvnstr = "sp"
        else:
            cgvnstr = ""
        newann.text = cgvnstr
        cgvntier.add_annotation(newann)
    
    return cgvntier

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
    to1tier = tgt.core.IntervalTier(st, et,"IU/Tone")

    for ann in wordtier._objects:
        newann = tgt.core.Annotation(ann.start_time, ann.end_time, text="")
        if (contains_chinese(ann.text)):
            if is_in_dict(cdict, ann.text):
                phone = get_phone(cdict, ann.text)
                newann.text = to_tone(phone)
                print(ann.text, phone, newann.text)
            #else:
            #    for c in ann.text:
                
        elif ann.text == "sp":
            newann.text = "sp"

        to1tier.add_annotation(newann)

    print(to1tier)
    return to1tier


# In[12]:


# Two tiers from original textgrid file
import copy

tg = read_txtgrid('03292019_3_001.textgrid.utf8')
ophonetier = tg.get_tier_by_name('phone')
owordtier =  tg.get_tier_by_name('word')

phonetier = ophonetier.get_copy_with_gaps_filled()
wordtier  = owordtier.get_copy_with_gaps_filled()

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
ipatier = ipa_tier(wordtier, phonetier)
cgtier = cgvn_tier(wordtier, phonetier)
ttier = tone_tier(wordtier, phonetier)

typetier = tgt.core.IntervalTier(st, et, "EU/Type")
#newtg.add_tier(typetier)

subjecttier = tgt.core.IntervalTier(st, et, "Subject")
#newtg.add_tier(subjecttier)

newtg.add_tier(ctier)
newtg.add_tier(etier)
newtg.add_tier(wordtier)
newtg.add_tier(phonetier)
#newtg.add_tier(postier)
newtg.add_tier(ipatier)
newtg.add_tier(cgtier)
newtg.add_tier(ttier)
newtg.add_tier(typetier)
newtg.add_tier(subjecttier)

write_txtgrid(newtg, "A0303.textgrid")


# In[13]:


import sys

def main():
    print('Number of arguments:', len(sys.argv), 'arguments.')
    if (len(sys.argv) != 2):
        print("Usage: sys.argv[0]: textfile, texgridfile")
    print('Argument List:', str(sys.argv))
    print("Hello World!")

if __name__ == "__main__":
    main()

