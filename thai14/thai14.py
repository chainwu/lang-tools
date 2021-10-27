#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8
""" Usage:
    python3 thai14.py directory
    
    This file takes a directory, process all .textgrid file and output output 14-tier txtgrid file
    directory: the directory that want to processed
    
    The output is textgrid_file+".14"
"""


# In[ ]:


from __future__ import print_function, division
from pypinyin import pinyin, lazy_pinyin, Style
import pandas as pd
import copy
import glob
import tgt
from googletrans import Translator
import itertools
import time

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
        
        zdf = pd.read_excel("zhuyin2ipa.xlsx")
    
        return(cdict, EHowTree, zdf)
    except Exception as e:
        print(e)
        exit(-1)

(cdict, EHowTree, zdf) = read_databases()

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

def is_ascii(check_str):
     return all(ord(c) < 128 for c in check_str)


# In[ ]:


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


# In[ ]:


SPECZ1=['ㄓ','ㄔ','ㄕ','ㄖ','ㄗ','ㄘ','ㄙ']
SPECZ2=['ㄧ','ㄨ','ㄩ']
CSPECZ2=['i','u','y']
FOURSOUNDS=['ˊ','ˇ','ˋ','˙']
DUOZ=['ㄧㄢ','ㄩㄢ','ㄧㄣ','ㄧㄥ','ㄨㄥ','ㄩㄥ']

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
    
def convertZH(zdf, zh):
    #print("searching", zh)
    x = zdf[zdf['Zhuyin']==zh].IPA.to_string(index=False)
    if x == "Series([], )":
        return ''
    else:
        return x
        #return x.replace(' ','')

def remove_foursounds(zh):
    z = zh
    for f in FOURSOUNDS:
        z = z.replace(f,'')
    return z

def is_duo(zh):
    for d in DUOZ:
        if d in zh:
            return True
    return False

def duo_convert(zdf, zh):
    #print("zh0",zh[0])
    matching = False
    for z in SPECZ2:
        #print("zzh", z, zh[0])
        if z == zh[0]:
            matching = True
            break
    
    if matching:
        #print("Converting zh", zh)
        return [convertZH(zdf, zh)]
    else:
        return [convertZH(zdf, zh[0]), convertZH(zdf, zh[1:]).replace('\n','')]
    
def convertIUY(z, last):
    if last:
        if z == 'ㄧ':
            return 'i'
        elif z == 'ㄨ':
            return 'u'
        else:
            return 'y'
    else:
        if z == 'ㄧ':
            return 'j'
        elif z == 'ㄨ':
            return 'w'
        else:
            return 'ɥ'

def zhuyin2ipa(zdf, zhuyin):
    zh=remove_foursounds(zhuyin)
    idx = 0
    zhlen = len(zh)
    
    if is_duo(zh):
        return(duo_convert(zdf, zh))
    
    IPAL=[]
    while (idx < zhlen):
        #print(idx)
        if zh[idx] in SPECZ1:
            if zhlen == 1:
                return ([convertZH(zdf, zh[idx]), 'ɨ'])
            else:
                IPAL.append(convertZH(zdf, zh[idx]))
                idx = idx + 1
                
        elif zh[idx] in SPECZ2:
            if idx == zhlen - 1:
                #The last one
                lc = convertIUY(zh[idx], True)
                IPAL.append(lc)
                return IPAL
            else:
                lc = convertIUY(zh[idx], False)
                IPAL.append(lc)
                idx = idx + 1
        else:
            IPAL.append(convertZH(zdf, zh[idx]))
            idx = idx + 1
            
    #print(IPAL)
    return IPAL

#zdf = read_zhuyin2upa_table()
z=zhuyin2ipa(zdf, " ㄗ˙")
print(z)


# In[ ]:


# In[6]:
SPLITLIST=['aj','ej','aw','ow','an','jɛn','ɥɛn','ən','in','aŋ','əŋ','iŋ','oŋ','joŋ']

def iu_tier(iut, wt, name):
    iut_tier = copy.deepcopy(iut)
    iut_tier.name = name
    #print(iut_tier)
    for ann in iut_tier._objects:
        #print(">>", ann.text)
        if ann.text == "":
            #print(ann.text, ann.start_time, ann.end_time)
            annlist = wt.get_annotations_between_timepoints(ann.start_time, ann.end_time)
            txt = ""
            for itm in annlist:
                txt = txt + itm.text
            #print(txt)
            ann.text = txt.replace("*","").replace("^","")
            if 'sp' in ann.text and 'sp' != ann.text:
                ann.text = ann.text.replace("sp", " ")
    
    #print(iut_tier)
    return iut_tier

def english_tier(iut, name, translator):
    et_tier = copy.deepcopy(iut)
    et_tier.name = name
    idx = 0
    for a in et_tier._objects:
        if (contains_chinese(a.text)): 
            print("Contains chinese:", a.text)
            # Need to add sleep here
            idx = idx + 1
            if idx % 10 == 0:
               time.sleep(10)
            else:
               time.sleep(2)
            tr = translator.translate(a.text, dest = 'en')
            a.text = tr.text
        else:
            print(a.text)
    #print(et_tier)
    return et_tier

def word_tier(wt, name):
    wt_tier = copy.deepcopy(wt)
    wt_tier.name = name
    for a in wt_tier._objects:
        if (contains_chinese(a.text)): 
            newannstr = ""
            #去 EHowNet 查詞性
            posp=EHowTree.searchWord(a.text)
            if posp:
                for w in posp:
                    #print(w.pos)
                    newannstr = newannstr + w.pos + " "
                #print(node)
                a.text = newannstr.rstrip()
            else:
                a.text = ""
        elif a.text != "sp":
            a.text=""
    #print(wt_tier)
    return wt_tier
            
def phone_tier(wt, name, zdf):
    ph_tier = tgt.core.IntervalTier(wt.start_time, wt.end_time, name)
    
    for a in wt._objects:
        if (contains_chinese(a.text)):
            print(a.text, end=" ")
            cccl = []
            for c in a.text:
                ccl = pinyin(c, style=Style.BOPOMOFO)
                #print(c, ccl[0][0], end=" ")
                cccl.append(ccl[0][0])

                #convert zhuying into IPA
                ipal = []
                for uccl in cccl:
                    #print(uccl)
                    uipa = zhuyin2ipa(zdf, uccl)
                    #print(uipa, end=" ")
                    #uuipa = [''.join(uipa[0:])]
                    ipal.append(uipa)
                
            flat_list = list(itertools.chain.from_iterable(ipal))
            flat_list= [f.replace(" ","") for f in flat_list]
            #print("flat list", flat_list)
            fl2 = []
            for f in flat_list:
                #print(f, end = " ")
                if f in SPLITLIST:
                    #print("In splitlist")
                    fl2.append(list(f))
                else:
                    fl2.append(f)
            fl2 = [x for x in fl2 if x !='']
            fl3 = []
            for item in fl2:
                if isinstance(item, list):
                    for item2 in item:
                        fl3.append(item2)
                else:
                    fl3.append(item)
            #fl2 = flat_list = [item for sublist in fl2 for item in sublist]
            print(fl3)
            #flat_list = [i.replace(" ", "") for i in flat_list if len(i) > 0]
            tintv = (a.end_time - a.start_time)/len(fl3)
            fstart = a.start_time
            fend = fstart+tintv
            for f in fl3:
                pann = tgt.core.Annotation(fstart, fend, f)
                ph_tier.add_annotation(pann)
                fstart = fstart + tintv
                fend = fend + tintv
                
        elif a.text == 'sp':
            pann = tgt.core.Annotation(a.start_time, a.end_time, "sp")
            ph_tier.add_annotation(pann)            
        else:
            pann = tgt.core.Annotation(a.start_time, a.end_time, "")
            ph_tier.add_annotation(pann)
    #print(ph_tier)  
    return ph_tier

def syllable_tier(wt, pt, name, zdf):
    syl_tier = copy.deepcopy(wt)
    syl_tier.name = name
    
    for a in syl_tier._objects:
        if contains_chinese(a.text):
            annlist=pt.get_annotations_between_timepoints(a.start_time, a.end_time)
            cgvn=""
            for aa in annlist:
                cgvn = cgvn + zdf[zdf['IPA']==aa.text].CGVN.to_string(index=False)
            
            a.text = cgvn.replace(" ","")
        elif a.text == 'sp':
            a.text = 'sp'

    return syl_tier
    
def tone_tier(wt, name):
    ttier = copy.deepcopy(wt)
    ttier.name = name
    for a in ttier._objects:
        if (contains_chinese(a.text)):
            cccl = []
            for c in a.text: 
                ccl = pinyin(c, style=Style.BOPOMOFO)
                cccl.append(ccl[0][0])
            
            pl = ""
            for p in cccl:
                pl = pl + foursounds(p) + " "
            
            a.text = pl.replace("  ", " ").rstrip()
        elif a.text != 'sp':
            a.text = ""
    print(ttier)
    return ttier

def type_tier(iust, name):
    typetier = copy.deepcopy(iust)
    typetier.name == name
    for a in typetier._objects:
        if "*" in a.text:
            a.text = "*"
        elif "^" in a.text:
            a.text = "^"
        elif a.text != 'sp':
            a.text = ""
            
    return typetier

def subject_tier(wt, name):
    subtier = copy.deepcopy(wt)
    subtier.name == name
    for a in subtier._objects:
        if a.text != 'sp':
            a.text = ""
    return subtier


# In[ ]:


# In[9]:

def parse_tiers(tg):
    iutier = tg.get_tier_by_name("IU/teacher")
    wstier = tg.get_tier_by_name("Word/teacher")
    iutone = tg.get_tier_by_name("IU/student")
    eutone = tg.get_tier_by_name("Word/student")
    return iutier, wstier, iutone, eutone

# Two tiers from original textgrid file

def thai14_main(txtgridr):
    #print(txtgridr)
    txtlist = glob.glob(txtgridr+"/*.TextGrid")
    print("File list", txtlist)
    translator = Translator()
    #print(translator)
    idx = 0
    for txtgridf in txtlist:
        if idx % 10 == 0:
            time.sleep(10)
        else:
            time.sleep(2)
        idx = idx + 1
        tg = tgt.io.read_textgrid(txtgridf, encoding='utf-8', include_empty_intervals=True)
        iuteacher, wordteacher, iustudent, wordstudent = parse_tiers(tg)
        #print(iuteacher)
        #print(wordteacher)
        #print(iustudent)
        #print(wordstudent)
        #for t in [iuteacher, wordteacher, iustudent, wordstudent]:
        #    remove_noises(t)
        #    filling_gaps(t)

        #align_tiers(wordtier, phonetier)

        st = tg.start_time
        et = tg.end_time

        #Construct tier contents
        new_iu_teacher = iu_tier(iuteacher, wordteacher, "IU/teacher") 
        #new_english_teacher = english_tier(new_iu_teacher, "English/teacher", translator) 
        new_word_teacher = word_tier(wordteacher, "Word/teacher")
        new_iu_phone = phone_tier(wordteacher, "IU/phone", zdf)
        new_iu_syllable = syllable_tier(wordteacher, new_iu_phone, "IU/syllable", zdf)
        new_iu_tone = tone_tier(wordteacher, "IU/tone")
        new_iu_student = iu_tier(iustudent, wordstudent, "IU/student")
        time.sleep(2)
        #new_english_student = english_tier(new_iu_student, "English/student", translator)
        new_word_student = word_tier(wordstudent, "Word/student")
        new_eu_phone = phone_tier(wordstudent, "IU/student", zdf)
        new_eu_syllable = syllable_tier(wordstudent, new_eu_phone, "EU/syllable", zdf)
        new_eu_tone = tone_tier(wordstudent, "EU/tone")
        new_eu_type = type_tier(iustudent, "EU/type")
        new_subject = subject_tier(new_iu_student, "Subject")
        
        # Construct textgrid
        newtg = tgt.core.TextGrid()        
        for nt in [new_iu_teacher, 
                   #new_english_teacher, 
                   new_word_teacher, 
                   new_iu_phone, 
                   new_iu_syllable, 
                   new_iu_tone, 
                   new_iu_student, 
                   #new_english_student,
                   new_word_student, 
                   new_eu_phone, 
                   new_eu_syllable, 
                   new_eu_tone, 
                   new_eu_type,
                   new_subject
                  ]:
            newtg.add_tier(nt)

        tgt.io.write_to_file(newtg, txtgridf+".14", format="long")


#thai14_main("./")

import sys

def main():
    if (len(sys.argv) != 2):
        print("Parameter error")
        print(__doc__)
        sys.exit(-1)
    else:
        txtgridr = sys.argv[1]
        thai14_main(txtgridr)
        
if __name__ == "__main__":
    main()
    


# In[ ]:





# In[ ]:




