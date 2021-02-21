#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

#zdf = pd.DataFrame()

def read_zhuyin2ipa_table():
    zdf = pd.read_excel("zhuyin2ipa.xlsx")
    return zdf

SPECZ1=['ㄓ','ㄔ','ㄕ','ㄖ','ㄗ','ㄘ','ㄙ']
SPECZ2=['ㄧ','ㄨ','ㄩ']
CSPECZ2=['i','u','y']
FOURSOUNDS=['ˊ','ˇ','ˋ','˙']
DUOZ=['ㄧㄢ','ㄩㄢ','ㄧㄣ','ㄧㄥ','ㄨㄥ','ㄩㄥ']

def is_ascii(check_str):
     return all(ord(c) < 128 for c in check_str)

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
        return x.replace(' ','')

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
        return convertZH(zdf, zh)
    else:
        return convertZH(zdf, zh[0])+convertZH(zdf, zh[1:]).replace('\n','')
    
def convertIUY(z):
    if z == 'ㄧ':
        return 'i'
    elif z == 'ㄨ':
        return 'u'
    else:
        return 'y'
    
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
                return (convertZH(zdf, zh[idx])+'ɨ')
            else:
                IPAL.append(convertZH(zdf, zh[idx]))
                idx = idx + 1
                
        elif zh[idx] in SPECZ2:
            if idx == zhlen - 1:
                #The last one
                lc = convertIUY(zh[idx])
                IPAL.append(lc)
                return IPAL
            else:
                IPAL.append(convertZH(zdf, zh[idx]))
                idx = idx + 1
        else:
            IPAL.append(convertZH(zdf, zh[idx]))
            idx = idx + 1
            
    #print(IPAL)
    return IPAL

def chine2ipa(df, zdf):
    col = df.columns.values
    row = df.index.values
    newdf = df.copy()

    for c in col:
        for r in row:
            ipastr=''
            x=str(df.loc[r,c]).replace(' ','')
            xx = pinyin(x, style=Style.BOPOMOFO)
            for item in xx:
                if not is_ascii(item[0]):
                    ipal=zhuyin2ipa(zdf, item[0])
                    fstr=foursounds(item[0])
                    for iipa in ipal:
                        ipastr = ipastr + iipa
                    ipastr = ipastr + foursounds(item[0])
                else:
                    ipastr = ipastr+item[0]
            newdf.loc[r,c] = str(df.loc[r,c])+' '+ipastr
    return newdf

def contains_o(x):
    for xt in x:
        if 'o|o' == xt or 'o|' in xt or '|o' in xt:
            return True

    return False

def page12_process(df, zdf, col, row):
    newdf = df.copy()
    for c in col:
        for r in row:
            #read excel and normalize it
            x=str(df.loc[r,c]).lstrip().strip().replace(' ','|').replace('oo','o|o').replace('xx','x|x').replace('??','?|?').replace('ox','o|x').replace('xo','x|o').split('-')
            #print("This is x:", x)
            if contains_o(x):
                #if the string contains an "o"

                #first we split the title
                ttlist = r.split()
                cl = []
                for t in ttlist:
                    term = list(t)
                    cl.append(term[0])
                    cl.append(term[1])
                #print(cl)
                
                #then we split the cell
                xl = []
                for xi in x:
                    xt = xi.split('|')
                    xl.append(xt[0])
                    if(len(xt) == 2):
                        xl.append(xt[1])

                #find the zhuying for the title
                cccl = []
                for xxl in cl:
                    ccl = pinyin(xxl, style=Style.BOPOMOFO)
                    cccl.append(ccl[0][0])

                #convert zhuying into IPA
                ipal = []
                for uccl in cccl:
                    #print(uccl)
                    uipa = zhuyin2ipa(zdf, uccl)
                    uuipa = [''.join(uipa[0:])]
                    fsound = foursounds(uccl)
                    ipal.append((uuipa[0]+fsound).strip())

                #If an "o" in the cell, replace it with IPA
                for i in range(len(xl)):
                    if 'o' in xl[i] :
                        xl[i] = ipal[i]
                        
                pstr = ''
                for i in range(len(xl)):
                    pstr = pstr + xl[i]
                    if i%2 == 0:
                        pstr = pstr + ' '
                    else:
                        pstr = pstr + '-'
                pstr = pstr[:-1]
                pstr = pstr.replace('x x', 'xx')
                #print(r, pstr)
            else :
                pstr = str(df.loc[r,c])
            
            newdf.loc[r,c] = pstr
            
    return newdf

def excel_page1(zdf):
    # to read just one sheet to dataframe:
    df = pd.read_excel('exp123.xlsx', sheet_name="實驗一", index_col=0, head=0)
    col = df.columns.values
    row = df.index.values

    newdf = page12_process(df, zdf, col, row)
    newdf.to_excel('實驗一.xlsx')


def excel_page2(zdf):
    # to read just one sheet to dataframe:
   df = pd.read_excel('exp123.xlsx', sheet_name="實驗二", index_col=0, head=0)
   col = df.columns.values
   row = df.index.values

   newdf = page12_process(df, zdf, col, row)
   newdf.to_excel('實驗二.xlsx')


from pypinyin import pinyin, lazy_pinyin, Style

#def excel_page3(zdf):
    #df = pd.read_excel('exp123.xlsx', sheet_name="實驗三(女)",index_col=0, head=0)
    #newdf = chine2ipa(df, zdf)
    #newdf.to_excel('實驗三(女).xlsx')


#def excel_page4(zdf):
    #df = pd.read_excel('exp123.xlsx', sheet_name="實驗三(男)",index_col=0, head=0)
    #newdf = chine2ipa(df, zdf)
    #newdf.to_excel('實驗三(男).xlsx')

def main():
    zdf = read_zhuyin2ipa_table()
    excel_page1(zdf)
    excel_page2(zdf)
    print(zhuyin2ipa(zdf, 'ㄒㄩ'))

    #excel_page3(zdf)
    #excel_page4(zdf)
    
if __name__ == '__main__':
    main()  # 或是任何你想執行的函式


