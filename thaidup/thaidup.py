#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python3
# coding: utf-8
""" Usage:
    python3 thaidup.py directory
    
    This file takes a directory, process all .textgrid file and output terms that are identical
    between layer 1 and 7
    directory: the directory that want to processed
    
    The output is textgrid_file+".dup"
"""


# In[2]:


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

def listprint(l):
    for item in l:
        #print(item)
        print(item.text, end="")
    print(" ", end="")


# In[3]:


import tgt
import glob

def thaidup_main(txtgridr):
    #print(txtgridr)
    txtlist = glob.glob(txtgridr+"/*.14")
    #print("File list", txtlist)
    #translator = Translator()
    #print(translator)
    for txtgridf in txtlist:
        print("[",txtgridf,"]")
        tg = tgt.io.read_textgrid(txtgridf, encoding='utf-8', include_empty_intervals=True)
        tier1 = tg.get_tier_by_name("IU/teacher")
        tier3 = tg.get_tier_by_name("Word/teacher")
        tier4 = tg.get_tier_by_name("IU/phone")
        tier5 = tg.get_tier_by_name("IU/syllable")
        tier6 = tg.get_tier_by_name("IU/tone")
        #print(first_tier)
        tier7 = tg.get_tier_by_name("IU/student")
        #print(stier)
        checked_term=[]
        for a in tier1._objects:
            if contains_chinese(a.text) and len(a.text) <=2 and not a.text in checked_term:
                #print(a.text, end=": ")
                match = False
                for b in tier7._objects:
                    if a.text == b.text:
                        print(a.text, ": ", end="")
                        match=True
                        break
                if match:
                    checked_term.append(a.text)
                    #dur = 0
                    cnt = 0
                    for c in tier1._objects:
                        if c.text == a.text:
                            cnt = cnt + 1
                    print("token", cnt, ",", end=" ")

                    #-----------------
                    for c in tier1._objects:
                        if c.text == a.text:
                            print((c.end_time - c.start_time)*1000, " msec, ", end=" ")
#                   print("token", cnt, ",", end=" ")
    
                    a3 = tier3.get_annotations_between_timepoints(a.start_time, a.end_time)
                    a4 = tier4.get_annotations_between_timepoints(a.start_time, a.end_time)
                    a5 = tier5.get_annotations_between_timepoints(a.start_time, a.end_time)
                    a6 = tier6.get_annotations_between_timepoints(a.start_time, a.end_time)
                    print("Tier3=", end=""), listprint(a3)
                    print("Tier4=", end=""), listprint(a4)
                    print("Tier5=", end=""), listprint(a5)
                    print("Tier6=", end=""), listprint(a6)
                    print(";", end=" ")
                    
                    cnt = 0
                    for d in tier7._objects:
                        if d.text == a.text:
                            cnt = cnt + 1
                    print("Student: token", cnt,  end=" ")
                    for d in tier7._objects:
                        if d.text == a.text:
                            print((d.end_time-d.start_time) * 1000, "ms", end=" ")
                    print()


# In[4]:


thaidup_main("06152018")


# In[5]:


thaidup_main("06182018")


# In[23]:


import sys

def main():
    if (len(sys.argv) != 2):
        print("Parameter error")
        print(__doc__)
        sys.exit(-1)
    else:
        txtgridr = sys.argv[1]
        thaidup_main(txtgridr)
        
if __name__ == "__main__":
    main()
    


# In[ ]:




